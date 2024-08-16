export function changeSort(currentSort, sortKey, isDescending) {

    return {
      key: sortKey || currentSort.key, 
      descending: isDescending ?? !currentSort.descending  
    }
  
  }

// export function pluralize(amount, singular, plural) {
//     return amount > 1 || amount === 0 ? plural : singular;
// }

export function pluralize(amount, subject) {
    let singular = subject
    let plural = subject
    if (subject.includes('|')) {
        plural = subject.split('|')
        singular = plural[0]
        plural = plural[1]
    }
    return amount > 1 || amount === 0 ? plural : singular;
}

export function capitalize(data) {
    const capitalized = [];
    data.split(' ').forEach(word => {
      capitalized.push(
        word.charAt(0).toUpperCase() +
        word.slice(1).toLowerCase()
      );
    });
    return capitalized.join(' ');
}

export function formatColumnTitle(str) {
    return capitalize(str.replace('_', ' '))
}

// Function to add styles to the head of the document
export function addStyles(styles) {
    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
};


// export const convertArraysToJSON = (obj) => {
//   for (const key in obj) {
//     if (Array.isArray(obj[key])) {
//       obj[key] = JSON.stringify(obj[key])
//     } else if (typeof obj[key] === 'object' && obj[key] !== null) {
//       convertArraysToJSON(obj[key])
//     }
//   }
// }

export function formatDate(dateString) {
  let date = new Date(dateString);
  
  // Get day, month, and year
  let day = date.getDate().toString().padStart(2, '0');
  let month = (date.getMonth() + 1).toString().padStart(2, '0'); // Month is zero-indexed
  let year = date.getFullYear();
  
  // Construct short date format
  let shortDateFormat = `${month}/${day}/${year}`;
  
  return shortDateFormat;
}
