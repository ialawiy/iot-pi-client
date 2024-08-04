// helpers.js
export function formatTime(hour, minute) {
  // Helper function to format hours and minutes as hh:mm
  const formattedHour = hour.toString().padStart(2, '0');
  const formattedMinute = minute.toString().padStart(2, '0');
  return `${formattedHour}:${formattedMinute}`;
}

export function stringToRGB(inputString) {
  let hash = 0;
  for (let i = 0; i < inputString.length; i++) {
    const char = inputString.charCodeAt(i);
    hash = (char + (hash << 5) - hash) & 0xFFFFFFFF;
  }

  const r = (hash & 0xFF0000) >> 16;
  const g = (hash & 0x00FF00) >> 8;
  const b = hash & 0x0000FF;

  return [r, g, b];
}

export function createTimeArray(interval) {
	const timesArray = [];
	for (let hour = 0; hour < 24; hour++) {
	  for (let minute = 0; minute < 60; minute += interval) {
		timesArray.push(formatTime(hour, minute));
	  }
	}
	//console.log(timesArray)
	return timesArray
}

  // Function to convert camelCase to Sentence case
  export function toSentenceCase(str) {
    return str.replace(/([A-Z])/g, " $1").replace(/^./, function (str) {
      return str.toUpperCase();
    });
  }