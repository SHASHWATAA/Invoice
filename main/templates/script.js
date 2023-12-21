function updateCheckboxes(checkbox) {
    const companyName = checkbox.dataset.company;
    const dayName = checkbox.name;
    const checkboxes = document.getElementsByName(dayName);

    // Uncheck all checkboxes with the same day name as the one that was clicked
    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].dataset.company !== companyName) {
            checkboxes[i].checked = false;
        }
    }
}

const spinnerUrl = 'loading.gif';
const checkmarkUrl = 'check.gif';

// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:5000');

// Connection opened
socket.addEventListener('open', function (event) {
    console.log('Connected to the WS Server!')
});

// Connection closed
socket.addEventListener('close', function (event) {
    console.log('Disconnected from the WS Server!')
});

socket.addEventListener('message', function (event) {
  console.log('Message from server ', event.data);
  const messages = document.getElementById('messages');
  const li = document.createElement('li');
  const [logMessage, status] = event.data.split(': ');
  li.textContent = logMessage;

  if (status === 'Running....') {
    const spinner = document.createElement('img');
    spinner.setAttribute('src', spinnerUrl);
    spinner.setAttribute('alt', 'Loading...');
    spinner.setAttribute('id', logMessage+'spinner');
    spinner.setAttribute('class', 'spinner');
    li.appendChild(spinner);
    messages.appendChild(li);

  } else if (status === 'Completed') {
        const spinner = document.getElementById(logMessage+'spinner');
        const checkMark = document.createElement('img');
        checkMark.setAttribute('src', checkmarkUrl);
        checkMark.setAttribute('alt', 'Completed');
        checkMark.setAttribute('class', 'checkmark');
    if (spinner == null){
        li.appendChild(checkMark);
        messages.appendChild(li);
    }else{
        try {
            spinner.parentNode.replaceChild(checkMark, spinner);
        } catch (TypeError) {
            //pass
            log('mas')
        }
    }
  } else if (status === 'canvas_invoice') {
        img_src = logMessage;
        const canvas_invoice = document.createElement('img');
        canvas_invoice.setAttribute('src', '.' + img_src);
        canvas_invoice.setAttribute('class', 'invoice');
        li.appendChild(canvas_invoice);
        messages.appendChild(li);
  } else if (status === 'cyrus_invoice') {
        img_src = logMessage;
        const canvas_invoice = document.createElement('img');
        canvas_invoice.setAttribute('src', '.' + img_src);
        canvas_invoice.setAttribute('class', 'invoice');
        li.appendChild(canvas_invoice);
        messages.appendChild(li);
  }


});

// Send a msg to the websocket
const sendMsg = () => {
  let days = {};

  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  if (checkboxes !== null) {
    checkboxes.forEach(function(checkbox) {
      if (checkbox.checked) {
        const company = checkbox.dataset.company;
        const day = checkbox.name;
        if (!days.hasOwnProperty(company)) {
          days[company] = [];
        }
        days[company].push(day);
      }
    });
  }
    socket.send("run@@@"+JSON.stringify(days));
}

window.onload = function() {
    const confirmCheckbox = document.querySelector('#confirmCheckbox');
    const outputButton = document.querySelector('#outputButton');

    confirmCheckbox.addEventListener('change', function() {
        outputButton.disabled = !this.checked;
    });
}