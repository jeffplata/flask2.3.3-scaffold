//vueSearchInput.js

const template = `
<div class="input-group">
<input
  ref="searchInputRef"
  type="text"
  class="form-control"
  placeholder="Search..."
  v-model="searchText"
  @input="debouncedSearch"
/>
<button class="btn btn-outline-secondary" type="button" @click="clearSearch">
  <i class="fa fa-x"></i>
</button>
</div>
`

const {ref, watch} = Vue;

const vueSearchInput = {
    setup(props, ctx) {
        const searchText = ref('')
        const searchInputRef = ref(null)

        const debouncedSearch = _.debounce(() => {
            // console.log('searching for: ', searchText.value)
            ctx.emit('searchChanged', searchText.value)
        }, 500)
        
        watch( searchText, () => {
            debouncedSearch()        
        })

        const clearSearch = () => {
            searchText.value = ''
            searchInputRef.value.focus()
        }

        return {
            searchText, clearSearch, debouncedSearch, searchInputRef,
        }
    },
    template: template,
}

export default vueSearchInput