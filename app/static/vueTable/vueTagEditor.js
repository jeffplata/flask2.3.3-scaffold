//vueTagEditor.js

const template =`
    <div class="row my-1">
        <div class="col-auto" style="margin:0px -20px 5px 0px">

            <span v-for="(tag, index) in tagsUsed" class="badge bg-secondary">[[tag.name]] 
                <button type="button" @click="deleteTag(index)" class="btn text-light" aria-label="Close">
                <span aria-hidden="true">&times;</span></button>
            </span>
        </div>
        <div class="col-auto">
            <input type="search" v-model="tagInputText" 
                @keydown.enter.prevent="onEnter"
                @keydown="onKeyDown"
                @click="toggleDropdownMenu"
                class="form-control form-control-sm" placeholder="Select role..." 
            />
            <div >
                <ul v-if="menuDroppedDown" :class="['dropdown-menu', {show:menuDroppedDown}]">
                    <li v-for="(tag, index) in tagsSelection" 
                     :key="index"
                     :class="['dropdown-item', {active : index == currentIndex}]" 
                     @click="onSelectItem(tag)">[[tag.name]]</li>
                </ul>
            </div>
        </div>
    </div>
`

const styles = `
    .badge {
        display: inline-flex; /* Change the display to flex */
        align-items: center; /* Align items vertically */
        margin-right: 2px;
        padding: 2px 5px;
    }
    .badge button {
        padding: 0px 0px 0px 5px; /* Adjust as needed */
    }
    .dropdown-item.active {
        background-color: #e9ecef;
        color: #212529;
    }
`
// Function to add styles to the head of the document
const addStyles = (styles) => {
    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
};

addStyles(styles); // Adding styles to the head

const {ref, computed, watch, onMounted} = Vue;

const vueTagEditor = {
    props: {
        allTags:{type: Array, default: () => []}, 
        tagsUsed:{type: Array, default: () => []}
    },
    setup(props) {

        const tagsUsed = ref([])
        const tagInputText = ref('')
        const tagsSelection = ref([])
        const menuDroppedDown = ref(false)
        const currentIndex = ref(-1)
        const availableTags = ref([])
        const allTags = props.allTags

        tagsUsed.value = props.tagsUsed
        tagsSelection.value = allTags
        
        const getAvailableTags = (allTags, tagsUsed) => {
            const usedIds = tagsUsed.map(tag => tag.id)
            // return allTags.filter(tag => !tagsUsed.includes(tag))
            return allTags.filter(tag => !usedIds.includes(tag.id))
        }
        availableTags.value = getAvailableTags(allTags, tagsUsed.value)
        
        const filterTags = (filterText) => {
            if (filterText == '') {
                tagsSelection.value = []
            } else {
                tagsSelection.value = availableTags.value.filter(tag => 
                    tag.toLowerCase().includes(filterText.toLowerCase()))
            }
        }

        const deleteTag = (index) => {
            tagsUsed.value.splice(index,1)
            availableTags.value = getAvailableTags(allTags, tagsUsed.value)
            tagsSelection.value = availableTags.value
        }

        const onEnter = (event) => {
            event.preventDefault()

            const trimmedInput = tagInputText.value.trim()
            const hasSelection = tagsSelection.value.length >0
            const isDropdownOpen = menuDroppedDown.value

            if (!trimmedInput && !isDropdownOpen) {
                tagsSelection.value = availableTags.value
                currentIndex.value = 0
                menuDroppedDown.value = true
                return
            }

            if (isDropdownOpen && hasSelection) {
                onSelectItem(tagsSelection.value[currentIndex.value])
                return
            }

            if (trimmedInput && hasSelection) {
                onSelectItem(tagsSelection.value[currentIndex.value])
            }
        }

        const onKeyDown = (event) => {
            if (menuDroppedDown.value && tagsSelection.value.length > 0) {
                if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    currentIndex.value = (currentIndex.value + 1) % tagsSelection.value.length;
                } else if (event.key === 'ArrowUp') {
                    event.preventDefault();
                    currentIndex.value = (currentIndex.value - 1 + tagsSelection.value.length) % tagsSelection.value.length;
                }
            }
        };

        const toggleDropdownMenu = () => {
            menuDroppedDown.value = !menuDroppedDown.value
            if (menuDroppedDown.value) {
                if (tagInputText.value == '') {
                    tagsSelection.value = availableTags.value
                    currentIndex.value = 0
                } else {
                    filterTags()
                }
            }
        }

        const onSelectItem = (tag) => {
            tagsUsed.value.push(tag)
            tagInputText.value = ''
            tagsSelection.value = []
            availableTags.value = availableTags.value.filter(item => item !== tag)
            currentIndex.value = -1
            menuDroppedDown.value = false
        }

        watch( tagInputText, () => {
            filterTags(tagInputText.value)
            let len = tagsSelection.value.length
            menuDroppedDown.value = len > 0
            currentIndex.value = len > 0 ? 0 : -1
        })

        return {
            tagInputText, tagsUsed, deleteTag, onEnter, onSelectItem, 
            tagsSelection, onKeyDown, toggleDropdownMenu, menuDroppedDown,
            currentIndex,
        }
    },
    template: template,
    delimiters: ['[[',']]'],
    styles: styles,
}

export default vueTagEditor;