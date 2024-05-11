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