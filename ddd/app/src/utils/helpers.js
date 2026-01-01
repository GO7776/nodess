exports.sanitizeFilename = (name) =>
  name.replace(/[<>:"/\|?*]/g, '_').replace(/\.+$/, '').slice(0, 200);
