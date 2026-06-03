const socket = io();




socket.on('join_room', (data) => {
    console.log('Connected to server');
});


socket.on('leave_room', (data) => {
    console.log('Disconnected from server');
});