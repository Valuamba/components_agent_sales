document.addEventListener('DOMContentLoaded', function () {
    // Create a new button
    var chatButton = document.createElement('button');
    chatButton.textContent = 'Open Chat';
    chatButton.style.marginLeft = '20px';

    // Add an event listener to the button
    chatButton.addEventListener('click', function () {
        window.location.href = '/chat/admin_room/'; // URL to your chat interface
    });

    // Find the header element or any other part of the admin where you want to add the button
    var header = document.querySelector('.dashboard-header') || document.querySelector('#header');

    // Append the button to the header
    if (header) {
        header.appendChild(chatButton);
    }
});
