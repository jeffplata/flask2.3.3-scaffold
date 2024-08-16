//vueAddItemPanel.js

import { addStyles } from './vueTableUtils.js';

const template = `
    <div style="position: relative;">
    <div class="input-group input-group-sm" >
      <input 
       type="text"
       class="form-control" 
       :placeholder=computedPlaceholder
       ref="searchInputRef"
       v-model="searchText"
       >
      <button 
       :class="[buttons.btnOk.inactive ? buttons.btnOk.inactiveClass : buttons.btnOk.activeClass]"
       type="button"
       @click.stop="onAddItem">
       <i class="fas fa-check"></i> {{buttons.btnOk.showLabel ? buttons.btnOk.label : ""}}</button>
      <button 
       :class="[buttons.btnCancel.inactive ? buttons.btnCancel.inactiveClass : buttons.btnCancel.activeClass]"
       type="button"
       @click.stop="clearSearch">
       <i class="fas fa-x"></i></button>
    </div>
    
      <div 
       v-show="selectionsOpen" 
       id="selectionsDiv" 
       ref="selectionsDivRef"
       style="position: absolute; z-index: 1000; " 
       class="bg-body rounded-2 border"
       >
        <ul class="list-group">
            <li class="list-group-item"
                style="cursor: default;"
                v-for="val, key in items" :key="key" 
                @click="onSelectItem(key)">{{val.name}}</li>
        </ul>
        <div v-if="selectionInfo" v-text="selectionInfo" class="fw-bold p-3"></div>
      </div>

    </div>
`

const styles = `
    ul li:hover {
        background-color: #e9ecef;
    }
`
addStyles(styles)

const {ref, toRefs, reactive, watch, watchEffect, onMounted, onUnmounted, computed } = Vue;

const vueAddItemPanel = {
    props: ['placeholder','lookupUrl', 'linkFields'],
    setup(props, ctx) {
        const { placeholder, lookupUrl, linkFields } = toRefs(props)
        const searchText = ref('')
        const searchInputRef = ref(null)
        const selectionsDivRef = ref(null)
        const documentRef = ref(null)
        const selectionsOpen = ref(false)
        const selectedItemFlag = ref(false)
        const isSearching = ref(false)
        const items = ref([])
        const itemsFoundAtSource = ref(0)
        const selectedItem = ref({
            id: -1,
            name: '',
        })
        const buttons = reactive({
            btnOk : {
                label : 'Add',
                showLabel : false,
                inactive : true,
                inactiveClass : "btn btn-outline-secondary disabled text-muted",
                activeClass : "btn btn-success"
            },
            btnCancel : {
                inactive : true,
                inactiveClass : "btn btn-outline-secondary disabled text-muted",
                activeClass : "btn btn-outline-secondary"
            }
        })
        
        const computedPlaceholder = computed(() => {
            return placeholder.value || 'Select an item to add...'
        })

        const selectionInfo = computed(() => {
            const itemsLength = items.value.length
            if (isSearching.value) {
                return 'Searching...'
            } else {
                if (itemsLength === 0) {
                    return 'No match found.'
                } else if (itemsLength < itemsFoundAtSource.value) {
                    return `Showing ${items.value.length} of ${itemsFoundAtSource.value}`    
                } else {
                    return ''
                }
            }
        })

        const isShowSelectionInfo = computed(() => {
            return items.value && items.value.length > itemsFoundAtSource.value
        })

        const performSearch = async () => {
            if (searchText.value.trim() === '') { return }
            try {
                const url = `${lookupUrl.value}/lookup?searchText=${searchText.value}&linkFields=${linkFields.value}`
                const response = await axios.get(url)
                isSearching.value = false
                const data = response.data
                items.value = data.data
                itemsFoundAtSource.value = data.totalRows
            } catch (error) {
                console.log('Error in lookup get:', error)
            }
        }

        // note: debounce is from lodash
        const debouncedSearch = _.debounce(() => {
            // ctx.emit('searchChanged', searchText.value)
            performSearch()
        }, 500)

        const handleClickOutsideSelection = (event) => {
            if (
                selectionsDivRef.value &&
                searchInputRef.value &&
                !selectionsDivRef.value.contains(event.target) &&
                !searchInputRef.value.contains(event.target)
            ) {
                selectionsOpen.value = false
            }
        }
        
        onMounted(() => {
            documentRef.value = document
            documentRef.value.addEventListener('click', handleClickOutsideSelection)
        })

        onUnmounted(() => {
            documentRef.value.removeEventListener('click', handleClickOutsideSelection)
        })

        watch( searchText, () => {
            if (selectedItemFlag.value) {
                selectedItemFlag.value = false
                return
            }
            buttons.btnCancel.inactive = searchText.value.trim() === ''
            buttons.btnOk.inactive = true
            debouncedSearch()
            selectedItem.value.id = -1
            selectionsOpen.value = searchText.value.trim() !== ''
            isSearching.value = searchText.value.trim() !== ''
        })

        watchEffect( () => {
            if (selectionsDivRef.value && searchInputRef.value) {
                selectionsDivRef.value.style.width = `${searchInputRef.value.offsetWidth}px`
            }
        })

        const getBtnOkInactiveState = () => buttons.btnOk.inactive
        watch( getBtnOkInactiveState, (nv,ov) => {
             buttons.btnOk.showLabel = !nv
        })

        const onSelectItem = (rowIndex) => {
            selectedItem.value.id = items.value[rowIndex].id
            selectedItem.value.name = items.value[rowIndex].value
            searchText.value = items.value[rowIndex].name
            selectionsOpen.value = false
            selectedItemFlag.value = true
            buttons.btnOk.inactive = false
        }

        const onAddItem = () => {
            if (selectedItem.value.id > -1) {
                ctx.emit('itemSelected', selectedItem.value.id)
                selectedItem.value.id = -1
                searchText.value = ''
                buttons.btnOk.inactive = true
                searchInputRef.value.focus()
            }
        }

        const clearSearch = () => {
            searchText.value = ''
            searchInputRef.value.focus()
            buttons.btnOk.inactive = true
            buttons.btnCancel.inactive = true
            items.value = []
            selectedItem.value.id = -1 
            selectionsOpen.value = false
        }

        return {
            searchText, clearSearch, debouncedSearch, searchInputRef,
            buttons, selectionsDivRef, items, onSelectItem, selectionsOpen,
            onAddItem, computedPlaceholder, lookupUrl, selectionInfo,
            itemsFoundAtSource, isShowSelectionInfo,
        }
    },
    template: template,
    styles: styles,
}

export default vueAddItemPanel