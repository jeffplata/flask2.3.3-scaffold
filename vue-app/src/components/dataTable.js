import { ref, watch } from 'vue';

export default function useDataTable() {
    const flashMessage = ref('Here data-table will rise.')
    const flashMessageVariant = ref('warning')
    var adding = ref(false)
    var editing = ref(false)
    var title =  ref('user|users')
    var title_s
    var items = ref([])
    var fields = ref([])
    var currentPage = ref(1)
    var perPage = ref(null)
    var totalRows
    var perPageOptions = ref([3,5,10,20,30,50,100])
    var selected = ref([])
    var sortBy = ref(''), sortDesc = ref(false)
    var filter

    items.value = [{id:1, 'name':'John', 'handle':'bob'},
        {id:2,'name':'allan','handle':'sap'},
        {id:3,'name':'kay','handle':'lank'},
        {id:4,'name':'archivald','handle':'zinc'},
        {id:5,'name':'terry','handle':'samayp'},
    ]

    items.value.forEach(el => {
        el.selected = false
    })

    // totalRows = items.value.length
    totalRows = 123

    fields.value = ['id', {'key':'name', 'sortable':'true'}, 
        {'key':'handle', 'sortable':true}, 'selected']

    fields.value.forEach(el => {
        if (typeof el!='string') {
            el.sortdesc = false
        }
    });

    let optionN = perPageOptions
    perPageOptions.value = optionN.value.map(n => ({value: n, label: `${n} items`}))
    perPage.value = JSON.parse(localStorage.getItem('perPage')) || '10'


    watch(perPage, (newVal, oldVal) => {
        if (typeof oldVal != 'undefined') {
            currentPage = 1
            // fetchData('page')
            localStorage.setItem('perPage', JSON.stringify(newVal));
        }
    })

    
    function unselectRows(exemptRow) {
        for (let i=0; i < items.value.length; i++) {
          if ((exemptRow !== undefined) && (i !== exemptRow)) {
            if (items.value[i].selected) {
              items.value[i].selected = false
            }
          }
        }
      }

    function onRowSelected(items) {
        selected.value = items
    }

    function onFiltered() {

    }

    function onSortChanged() {

    }

    function onSubmitForm() {

    }

    function onPageChange(page) {
        currentPage = page
        // fetchData('page')
    }

    return {
        flashMessage,
        flashMessageVariant,
        adding,
        editing,
        title,
        title_s,
        selected,
        items, fields,
        currentPage, perPage, perPageOptions, totalRows,
        onRowSelected, onFiltered, onSortChanged, onSubmitForm,
        onPageChange, unselectRows,
        sortBy, sortDesc, filter,
    }
}