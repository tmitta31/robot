determiningStall = function(durationInSeconds = 10) {
  // This outer interval checks for client activity repeatedly at specified intervals.
  setInterval(() => {
    io.emit('are_clients_active', 'Clients are you there?');
    activeUserReplied = false;

    // We use a setTimeout instead of setInterval to create a single delayed check
    // after the duration has passed, rather than creating repeated checks.
    setTimeout(() => {
      if (!activeUserReplied) {
        thereIsAnActiveUser = false;
        io.emit('stall', 'stall?');
      }
    }, (durationInSeconds * 60 * 1000) / 2);
  }, durationInSeconds * 60 * 1000);
}


determiningStall()