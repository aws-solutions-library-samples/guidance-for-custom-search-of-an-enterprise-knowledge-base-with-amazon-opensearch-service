export const readTimestamp = (timestamp) => {
  if (timestamp === undefined || Number.isNaN(Number(timestamp))) {
    return 'N/A';
  }
  return new Date(Number(timestamp)).toLocaleString().slice(0, 24);
};
