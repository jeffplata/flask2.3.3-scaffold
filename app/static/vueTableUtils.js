export function changeSort(currentSort, sortKey, isDescending) {

    return {
      key: sortKey || currentSort.key, 
      descending: isDescending ?? !currentSort.descending  
    }
  
  }