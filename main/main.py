import json
import time
from datetime import datetime, date, timedelta

import asposecells
import jpype
from pandas import DataFrame as df, ExcelWriter
from pdf2image import convert_from_path

import timesheet_json
from send_message import send_data


def get_worked_data(json_data, _required_dates):
    """
    :rtype: dict
    """
    d = json.loads(json_data, strict=False)
    worked_data = {'data': []}

    for required_date in _required_dates:
        # required dates are the days of the week we and the output is in the format to %Y-%m-%d.
        # datetime.fromisoformat(x['Date']).strftime('%Y-%m-%d') is the current date in the API formatted to %Y-%m-%d
        # need to do this because api displays more than what we need.

        var = [x for x in d if datetime.fromisoformat(x['Date']).strftime('%Y-%m-%d') == required_date]

        if len(var) == 0:
            invoice_date = datetime.fromisoformat(required_date).strftime('%Y/%m/%d')
            day = datetime.fromisoformat(required_date).strftime('%A')
            net_worked_seconds = 0
            time_in = ""
            break_start = ""
            break_end = ""
            time_out = ""
            total_hours = "00:00"

            worked_datum = make_invoice_json_data(invoice_date, day, time_in, break_start, break_end, time_out,
                                                  total_hours, net_worked_seconds)
            worked_data['data'].append(worked_datum)

        else:
            start = datetime.fromisoformat(var[0]['StartTimeLocalized'])
            end = datetime.fromisoformat(var[0]['EndTimeLocalized'])

            worked_seconds = (end - start).seconds
            try:
                break_seconds = var[0]['Slots'][0]['intEnd'] - var[0]['Slots'][0]['intStart']
            except IndexError:
                break_seconds = 0

            net_worked_seconds = worked_seconds - break_seconds
            worked_h_m_s = str(timedelta(seconds=net_worked_seconds))
            y = worked_h_m_s.split(":")
            worked_h_m = f"{y[0]}:{y[1]}"

            invoice_date = datetime.fromisoformat(var[0]['Date']).strftime('%Y/%m/%d')
            day = datetime.fromisoformat(var[0]['Date']).strftime('%A')
            time_in = start.strftime('%I:%M')

            if break_seconds == 0:
                break_start = "-"
                break_end = "-"
            else:
                break_start = "12:30"
                break_end = "1:00"

            time_out = end.strftime('%I:%M')
            total_hours = worked_h_m

            worked_datum = make_invoice_json_data(invoice_date, day, time_in, break_start, break_end, time_out,
                                                  total_hours, net_worked_seconds)

            worked_data['data'].append(worked_datum)

            # print(x['Date'], net_worked_seconds / 3600, worked_h_m)

    return worked_data


def get_week_dates(week):
    if week == 0:
        today = date.today()
    else:
        today = date.today() - timedelta(days=7)

    weekday = today.isoweekday()
    # The start of the week
    start = today - timedelta(days=weekday - 1)
    # build a simple range
    dates = [start + timedelta(days=d) for d in range(7)]
    dates = [str(d) for d in dates]

    return dates


def make_invoice_json_data(invoice_date, day, time_in, break_start, break_end, time_out, total_hours, worked_seconds):
    return {'Date': invoice_date, 'Day': day, "Time In": time_in, "Break Start": break_start, "Break End": break_end,
            "Time Out": time_out, "Total Hours": total_hours, "worked_seconds": worked_seconds}


def write_to_excel_template(template, _table, _rate, worked_days):
    with ExcelWriter(template, mode="a", engine="openpyxl", if_sheet_exists="overlay", ) as writer:

        # copying table so that original table is not changed.
        temp_table = _table.copy()

        # deleting days not worked in table
        for day in temp_table['Day']:
            if day not in worked_days:
                temp_table.loc[temp_table.Day == day, ["Time In", "Break Start", "Break End", "Time Out"]] = ""
                temp_table.loc[temp_table.Day == day, "Total Hours"] = "00:00"
                temp_table.loc[temp_table.Day == day, "worked_seconds"] = 0

        total_worked_seconds = int(temp_table["worked_seconds"].sum())
        temp_table = temp_table.drop(["worked_seconds"], axis=1)
        t = timedelta(seconds=total_worked_seconds)
        worked_h_m = f'{t.days * 24 + t.seconds // 3600:02}:{(t.seconds % 3600) // 60:02}'
        total_pay = _rate * (total_worked_seconds / 60 / 60)

        writer.sheets["Weekly Timesheet"].cell(17, 8, worked_h_m)
        writer.sheets["Weekly Timesheet"].cell(18, 8, _rate)
        writer.sheets["Weekly Timesheet"].cell(19, 8, total_pay)
        invoice_number = writer.sheets["Weekly Timesheet"].cell(6, 4).value
        writer.sheets["Weekly Timesheet"].cell(6, 4).value = writer.sheets["Weekly Timesheet"].cell(6, 4).value + 2

        temp_table.to_excel(writer, sheet_name="Weekly Timesheet", startcol=1, startrow=8, index=False, header=False)

        return


def convert_to_pdf(input_file_path):
    from asposecells.api import Workbook
    workbook = Workbook(input_file_path)
    worksheets = workbook.getWorksheets()
    sheet_index = worksheets.add()
    sheet = worksheets.get(sheet_index)
    page_setup = sheet.getPageSetup()
    page_orientation_type = asposecells.api.PageOrientationType
    page_setup.setOrientation(page_orientation_type.PORTRAIT)
    workbook.save(input_file_path.split("_")[1].split(".")[0] + ".pdf")


def convert_to_image(pdf_file_path):
    image = convert_from_path(pdf_file_path, dpi=200)[0]
    width, height = image.size
    image = image.crop((0, 200, width, height))
    image.save("./Invoices/" + datetime.now().strftime("%d-%m-%Y") + " Invoice " + pdf_file_path.split(".")[0] + ".png",
               "PNG")
    pass


async def invoice_generator(canvas_days, cyrus_days):
    await send_data("Connecting to deputy", "Running....")
    data = timesheet_json.using_selenium()
    await send_data("Connecting to deputy", "Completed")

    await send_data("Getting Week Dates", "Running....")
    required_dates = get_week_dates(1)
    table_data = get_worked_data(data, required_dates)

    await send_data("Getting Week Dates", "Completed")

    headings = ['Date', 'Day', "Time In", "Break Start", "Break End", "Time Out", "Total Hours", "worked_seconds"]
    rate = 30
    table = df.from_dict(table_data['data'])

    # print(table)
    canvas_template = "template_Canvas Home Interiors.xlsx"
    cyrus_template = "template_Cyrus Rugs.xlsx"
    # canvas_days = ["Tuesday"]
    # cyrus_days = ["Monday", "Wednesday", "Friday", "Thursday"]

    await send_data("Writing Canvas Template", "Running....")

    write_to_excel_template(canvas_template, table, rate, canvas_days)

    await send_data("Writing Canvas Template", "Completed")
    await send_data("Writing Cyrus Template", "Running....")

    write_to_excel_template(cyrus_template, table, rate, cyrus_days)

    await send_data("Writing Cyrus Template", "Completed")

    if not jpype.isJVMStarted():
        jpype.startJVM()

    await send_data("Converting Canvas Template To PDF", "Running....")
    convert_to_pdf(canvas_template)
    await send_data("Converting Canvas Template To PDF", "Completed")
    await send_data("Converting Cyrus Template To PDF", "Running....")
    convert_to_pdf(cyrus_template)
    # jpype.shutdownJVM()
    await send_data("Converting Cyrus Template To PDF", "Completed")

    await send_data("Converting Cyrus PDF To Image", "Running....")
    convert_to_image("Canvas Home Interiors.pdf")
    await send_data("Converting Cyrus PDF To Image", "Completed")
    await send_data("Converting Canvas PDF To Image", "Running....")
    convert_to_image("Cyrus Rugs.pdf")
    await send_data("Converting Canvas PDF To Image", "Completed")
    # time.sleep(0.5)
    await send_data("Invoice Generated", "Completed")


if __name__ == '__main__':
    pass