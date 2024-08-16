//vueSelectField.js

import { addStyles } from './vueTableUtils.js';

const template = `
  <div 
    style="position: relative;"
    role="combobox"
    aria-haspopup="listbox"
    :aria-expanded="isOpen"
  >
  
    <label class="form-label" for="mainInput">{{controlLabel}}</label>
    <input 
      type="text" 
      :value="selectedLabel"
      @input="updateValue"
      @click="toggleDropdown"
      @keydown="onMainInputKeyDown"
      class="form-select"
      readonly
      placeholder="Select an option"
      id="mainInput"
      ref="mainInputRef"
    />
    
      <div 
      v-show="isOpen" 
      id="selectionsDiv" 
      ref="selectionsDivRef"
      :style="{
        position: 'absolute',
        zIndex: 1000,
        overflowY: 'auto',
        maxHeight: maxHeight + 'px',
        width: inputWidth + 'px',
        top: showAbove ? null : '100%',
        bottom: showAbove ? bottomPosition : null,
        left: '0',
        backgroundColor: 'white',
        border: '1px solid black'
      }"
      class="bg-body rounded-2 border py-2 px-1 dropdown-transition"
    >
        <input
          id="searchInput"
          ref="searchInputRef"
          type="search"
          class="form-control form-control-sm mb-1"
          v-model="searchQuery"
          placeholder="Search for..."
          @keydown="handleKeyDown"
          @blur="handleBlur"
        >
        <ul class="list-group">
            <li v-for="val, key in filteredOptions" :key="key" 
                class="list-group-item list-group-item-compact"
                :class="{ highlighted : key === highlightedIndex }"
                style="cursor: default;"
                @click="onSelectItem(key)"
                @mouseover="handleOptionMouseOver(key)"
            >{{val.label}}</li>
        </ul>
        <div v-if="selectionInfo" v-text="selectionInfo" class="fw-bold p-2"></div>
      </div>

  </div>
`

const styles = `
  .list-group-item-compact {
    padding-top: 0.1rem;
    padding-bottom: 0.1rem;
  }
  .dropdown-transition {
  transition: max-height 0.3s ease-in-out, top 0.3s ease-in-out, bottom 0.3s ease-in-out;
  }
  .dropdown-transition {
    transition: max-height 0.3s ease-out;
  }
  .highlighted {
  background-color: #e0e0e0;
`
addStyles(styles)

const { ref, computed, onMounted, onUnmounted, watch, toRefs, nextTick, watchEffect } = Vue;

const vueSelectField = {
    props: ['modelValue','controlLabel','items'],
    emits: ['update:modelValue'],
    setup(props, { emit }) {
        
        const isOpen = ref(false)
        const searchQuery = ref('')
        const isSearching = ref(false)
        const mainInputRef = ref(null)
        const searchInputRef = ref(null)
        const documentRef = ref(null)
        const selectionsDivRef = ref(null)
        const options = ref([])
        const maxHeight = ref(0);
        const inputWidth = ref(0)
        const showAbove = ref(false);
        const bottomPosition = ref(null);
        const highlightedIndex = ref(-1)
        
        const updateValue = (selectedValue) => {
          emit('update:modelValue', selectedValue);
        };
        
        const {controlLabel, items} = toRefs(props)

        const modelValue = computed(() => props.modelValue)

        const selectedLabel = computed(() => {
          const selectedOption = options.value.find(option => option.value === modelValue.value);
          return selectedOption ? selectedOption.label : '';
        });

        const handleClickOutsideSelection = (event) => {
            if (
                selectionsDivRef.value &&
                mainInputRef.value &&
                !selectionsDivRef.value.contains(event.target) &&
                !mainInputRef.value.contains(event.target)
            ) {
                isOpen.value = false
            }
        }
    
        const calculatePosition = () => {
          if (!isOpen.value || !selectionsDivRef.value || !mainInputRef.value) {
            return;
          }
          
          const inputRect = mainInputRef.value.getBoundingClientRect();
          const spaceBelow = window.innerHeight - inputRect.bottom;
          const spaceAbove = inputRect.top;
          const contentHeight = selectionsDivRef.value.scrollHeight;
        
          showAbove.value = spaceBelow < contentHeight && spaceAbove > spaceBelow;
        
          const availableHeight = showAbove.value ? spaceAbove : spaceBelow;
          maxHeight.value = Math.min(availableHeight - 10, 300); // 10px for margin, max 300px
        
          // Ensure the width is set correctly
          inputWidth.value = mainInputRef.value.offsetWidth;
        
          // Calculate the position for when shown above
          if (showAbove.value) {
            bottomPosition.value = inputRect.height + 'px';
          } else {
            bottomPosition.value = null;
          }
        
        };

        const handleResize = () => {
          if (isOpen.value) {
            calculatePosition();
          }
        };

        const forceUpdate = () => {
          if (isOpen.value) {
            isOpen.value = false;
            nextTick(() => {
              isOpen.value = true;
            });
          }
        };
        
        onMounted(() => {
          documentRef.value = document;
          documentRef.value.addEventListener('click', handleClickOutsideSelection);
          window.addEventListener('resize', handleResize);
        
          nextTick(() => {
            if (mainInputRef.value) {
              inputWidth.value = mainInputRef.value.offsetWidth;
            }
          });

            if (typeof items.value === 'string') {
              // Remove the outer square brackets and split into individual tuples
              const dataString = items.value
              const tuples = dataString.slice(1, -1).split('), (');
  
              // Parse each tuple into an array
              const parsedData = tuples.map(tuple => {
                  const [id, name] = tuple.replace(/[()]/g, '').split(", '");
                  return [parseInt(id), name.replace(/'/g, '')];
              });
              parsedData.forEach((item) => {
                options.value.push({'value':item[0],'label':item[1]})
              })
  
            }
        })

        onUnmounted(() => {
            documentRef.value.removeEventListener('click', handleClickOutsideSelection)
            window.addEventListener('resize', handleResize);
        })

        const filteredOptions = computed(() => {
          if (searchQuery.value.trim() === '') {
            return options.value
          }
          return options.value.filter(option => 
            option.label.toLowerCase().includes(searchQuery.value.toLowerCase())
          )
        })

        watch(filteredOptions, (newValue) => {
          if (newValue && newValue.length > 0) {
            return highlightedIndex.value = 0
          }
          highlightedIndex.value = -1
        })
        
        watch(() => props.modelValue, (newValue) => {
          if (newValue !== undefined && options.value.length > 0) {
            const selectedOption = options.value.find(option => option.value === newValue);
            if (selectedOption) {
              updateValue(selectedOption.value);
            }
          }
        }, { immediate: true });

        watch(isOpen, (newValue) => {
          if (newValue) {
            nextTick(() => {
              calculatePosition();
            });
          } 
          else {
            searchQuery.value = ''
            if (mainInputRef.value) {
              mainInputRef.value.focus()
            }
          }
        });

        watch(searchQuery, (nv) => {
          if (isOpen.value) {
            isSearching.value = true
            debouncedSearch()
            isSearching.value = false
            nextTick(() => {
              if (isOpen.value) {
                calculatePosition();
              }
            });
          }
        })

        const selectionInfo = computed(() => {
          const optionsLength = filteredOptions.value.length
          if (isSearching.value) {
              return 'Searching...'
          } else {
              if (optionsLength === 0) {
                if (searchQuery.value !== '') {
                  return 'No match found.'
                } else {
                  return 'No data.'
                }
              } else if (optionsLength !== 0) {
                  return `Found ${optionsLength} out of ${options.value.length}`
              } else {
                  return ''
              }
          }
      })

        const handleOptionMouseOver = (key) => {
          highlightedIndex.value = key
        }

        const performSearch = () => {
          return filteredOptions
        }

        const debouncedSearch = _.debounce(() => {
            performSearch()
        }, 500)

        const onSelectItem = (rowIndex) => {
          const selectedValue = filteredOptions.value[rowIndex].value;
          updateValue(selectedValue);
          isOpen.value = false;
          // searchQuery.value = ''
        };

        const cycleItem = () => {
          const selectedValue = filteredOptions.value[highlightedIndex.value].value;
          updateValue(selectedValue);
        }
        
        const preventClose = (event) => {
            event.preventDefault()
        }

        const openDropdown = () => {
          isOpen.value = true
        }
        
        const toggleDropdown = () => {
          isOpen.value = !isOpen.value;
          if (isOpen.value) {
            nextTick(() => {
              setTimeout(() => {
                calculatePosition();
                if (searchInputRef.value) {
                  searchInputRef.value.focus();
                }
              }, 50);
            });
          }
        };
        
        const handleBlur = (event) => {
          if ((selectionsDivRef.value && selectionsDivRef.value.contains(event.relatedTarget)) ||
              (searchInputRef.value && searchInputRef.value.contains(event.relatedTarget)) ) {
            return; // Do nothing if focus is moving inside the dropdown
          }
          setTimeout(() => {
            isOpen.value = false
          }, 100)  // Allow time for the <li> onclick to process
        }

        const scrollToHighlighted = () => {
          nextTick(() => {
            if (highlightedIndex.value === 0) {
              scrollToSearchInputControl()
              return
            }
            const highlightedElement = document.querySelector('.highlighted');
            if (highlightedElement) {
              highlightedElement.scrollIntoView({
                block: 'nearest',
                behavior: 'smooth'
              });
            }
          });
        };

        const scrollToSearchInputControl = () => {
          nextTick(() => {
            searchInputRef.value.scrollIntoView({
              block: 'nearest',
              behavior: 'smooth'
            })
          })
        }

        const onMainInputKeyDown = (event) => {
          if (event.altKey) {
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
              toggleDropdown()
              return
            }
          }
          if (event.key.length === 1 && !event.ctrlKey && !event.altKey && !event.metaKey) {
            event.preventDefault()
            toggleDropdown()
            searchQuery.value = event.key
            searchInputRef.value.setSelectionRange(1,1)
            return
          }
          switch(event.key) {
            case 'ArrowDown':
              event.preventDefault();
              highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1);
              break;
            case 'ArrowUp':
              event.preventDefault();
              highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0);
              break;
            default:
              return
          }
          cycleItem()
        }

        const PAGE_DOWN_ITEMS = 10
        const handleKeyDown = (event) => {
          switch(event.key) {
            case 'ArrowDown':
              if (event.altKey) {
                toggleDropdown()
                break;
              }
              event.preventDefault();
              highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1);
              break;
            case 'ArrowUp':
              if (event.altKey) {
                toggleDropdown()
                break;
              }
              event.preventDefault();
              highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0);
              break;
            case 'PageDown':
              event.preventDefault();
              highlightedIndex.value = Math.min(highlightedIndex.value + PAGE_DOWN_ITEMS, filteredOptions.value.length - 1);
              break;
            case 'PageUp':
              event.preventDefault();
              highlightedIndex.value = Math.max(highlightedIndex.value - PAGE_DOWN_ITEMS, 0);
              break;
            case 'Home':
              event.preventDefault();
              highlightedIndex.value = 0;
              scrollToSearchInputControl()
              break;
            case 'End':
              event.preventDefault();
              highlightedIndex.value = filteredOptions.value.length - 1;
              break;
            case 'Enter':
              event.preventDefault();
              if (highlightedIndex.value >= 0) {
                onSelectItem(highlightedIndex.value)
              }
              break;
            case 'Escape' || 'Esc':
              event.preventDefault();
              searchQuery.value = ''
              isOpen.value = false
              break;
          }
          scrollToHighlighted();
        };


        return {
            openDropdown, toggleDropdown, handleBlur, updateValue,
            preventClose, onSelectItem,
            forceUpdate, handleOptionMouseOver, handleKeyDown, onMainInputKeyDown,
            isOpen, searchQuery, filteredOptions,
            selectionInfo, selectionsDivRef, mainInputRef, searchInputRef,
            modelValue, controlLabel, selectedLabel,
            maxHeight, inputWidth, showAbove, bottomPosition,
            highlightedIndex,
            // modelValue: computed(() => props.modelValue)
        }
    },
    template: template,
    styles: styles,
}

export default vueSelectField