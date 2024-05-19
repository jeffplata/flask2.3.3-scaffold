import { changeSort, formatColumnTitle, pluralize, capitalize } from './vueTableUtils.js';

const { ref, reactive, computed, watch, onMounted } = Vue;

const templateCache = ref(null)
if (!templateCache.value) {
    const response = await fetch('./static/vueTable.html')
    const templateText = await response.text()

    templateCache.value = templateText
}

const styles = `
        [v-cloak] {
            display: none;
        }

        .sort-off {
            color: lightgray
        }
    
        .sort-badge {
            cursor: pointer;
            float: right;
        }

        form label {
            font-weight: 600;
        }
`
// Function to add styles to the head of the document
const addStyles = (styles) => {
    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
};

addStyles(styles); // Adding styles to the head

const VueTable = {
    props: ['apiEndpoint', 'apiEditEndpoint', 'apiDeleteEndpoint'],
    emits: ['pageChanged', 'searchChanged'],
    setup(props) {
        const apiEndpointValue = props.apiEndpoint
        const editing = ref(false)
        const adding = ref(false)
        const selected = ref([])
        const selectedIndex = ref(-1)
        const flashMessage = ref('Welcome to VueTable.')
        const flashMessageVariant = ref('warning')
        const currentPage = ref(1)
        const perPage = ref(3)
        const perPageOptions = ref([3,5,10,20,30,50,100])
        const totalRows = ref(0)
        const filter = ref('')
        const fields = ref([])
        const items = ref([])
        const formData = reactive({})  // use Object.assign not formData.value = ...
        const undoData = reactive({})
        const formErrors = ref([])

        const entity = apiEndpointValue.split('/')[1]
        const title = ref('')
        const name_field = ref('')
        const fieldsOrder = ref([])

        const selectedName = computed(() => {
            return this.selected.value.length > 0 ? this.selected.value[0].name : '';
        })

        const titleSingular = computed(() => {return pluralize(1, title.value)})
        const titlePlural = computed(() => {return pluralize(2, title.value)})

        const sortState = ref({
            key: '',
            descending: true  
          })

        onMounted(() => {
            let optionN = perPageOptions.value
            perPageOptions.value = optionN.map(n => ({'value': n, 'text': `${n} items`}))
            perPage.value = JSON.parse(localStorage.getItem('perPage')) || 10
        })

        const fetchData = async (triggeredBy = '') => {
            const endPoint = `${apiEndpointValue}`
            const startIndex = (currentPage.value - 1) * perPage.value
      
            let sortArgs = ''
            let filterArgs = ''
      
            if (['filter', 'sort', 'perPage'].includes(triggeredBy)) {
              currentPage.value = 1
            }
      
            const pageArgs = `?start=${startIndex}&limit=${perPage.value}`
            filterArgs = `&filtertext=${filter.value}`
            sortArgs = `&sortby=${sortState.value.key}&sortdesc=${sortState.value.descending}`
                  
            try {
              const response = await axios.get(`${endPoint}${pageArgs}${filterArgs}${sortArgs}`)
              const data = response.data
      
              items.value = data.data
              fields.value = data.fieldnames
              totalRows.value = data.totalrows
              flashMessage.value = ''

              fieldsOrder.value = []
              fields.value.forEach((el, index) => {
                fieldsOrder.value.push(typeof el!=='string' ? el.key : el)
                if (typeof el!=='string') {
                    el.title = formatColumnTitle(el.key)
                    el.sortdesc = false
                } else {
                    fields.value[index] = formatColumnTitle(el)
                }
              });
      
              // get init data title and name_field
              try {
                const response = await axios.get(apiEndpointValue+'_init')
                const data = response.data

                title.value = data.title
                name_field.value = data.name_field
              } catch(error) {
                console.log('Failed to fetch init data.', error)
              }

            } catch (error) {
              console.error('Error fetching data:', error)
            }            
        }

        watch([currentPage], () => { fetchData() })

        watch(filter, () => { fetchData('filter') })

        watch(perPage, (nv, ov) => {
            fetchData('perPage')
            localStorage.setItem('perPage', JSON.stringify(nv));
        })

        watch(editing, (nv) => { 
          if (nv) {
            flashMessage.value = ''
          }
          formErrors.value = [] })

        function onClickSortBadge() {
            sortState.value = {key: '', descending: false}
            fetchData('sort')
        }

        function onHeaderClick(fld) {
            if (typeof fld!=='string') {
                sortState.value = changeSort(
                    sortState.value,
                    fld.key,
                    fld.key === sortState.value.key ? !sortState.value.descending : false
                  )
                fetchData('sort')
            }
        }

        function onClickAdd() {
          for (let key in formData) {delete formData[key]}
          editing.value = adding.value = true
        }

        function onClickRow(row, id) {
            editing.value = true
            selectedIndex.value = id
            selected.value = [row]
            Object.assign(formData, {...row})
            // Object.assign(undoData, {...row})
            Object.assign(undoData, structuredClone(_.cloneDeep(row)))
        }

        function saveEdit() {
        //     // use this to test only
        }

        function undoEdit() {
          flashMessage.value = ''
          // Object.assign( formData, null) // will not work
          for (let key in formData) {delete formData[key]}
          // items.value.splice(selectedIndex.value, 1, {...undoData})
          items.value.splice(selectedIndex.value, 1, structuredClone(_.cloneDeep(undoData)))
          selectedIndex.value = -1
          adding.value = editing.value = false
        }

        function onClickCloseAlert() {
            flashMessage.value = ''
        }

        function onPageChanged(newPage) {
            currentPage.value = newPage
        }

        function onSearchChanged(newSearch) {
            filter.value = newSearch
        }

        const axiosPost = async (url, bodyFormData) => {
            try {
                const response = await axios.post(url, bodyFormData, {
                  headers: { 'Content-Type': 'application/json' },
              })
                return response.data
            } catch (error) {
                console.error('Error in axiosPost:', error)
                throw error
            }
        }
  
        const submitForm = async (event) => {
            try {
              const url = `${props.apiEditEndpoint}`
              const bodyFormData = new FormData()
              let tempFormData = new FormData()
      
              if (adding.value) { formData.id = -1 }

              const convertArraysToJSON = (obj) => {
                for (const key in obj) {
                  if (Array.isArray(obj[key])) {
                    obj[key] = JSON.stringify(obj[key])
                  } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                    convertArraysToJSON(obj[key])
                  }
                }
              }
              Object.assign(tempFormData, formData)
              convertArraysToJSON(tempFormData)

              for (const [key, value] of Object.entries(tempFormData)) {
                bodyFormData.append(key, value)
              }
      
              const response = await axiosPost(url, bodyFormData)
      
              if (response.message) {
                // this is surely an error message from flask
                flashMessageVariant.value = 'warning'
                flashMessage.value = response.message
              }
      
              if (response.result === 'failed') {
                formErrors.value = response.errors
              } else {
                if (adding.value) {
                  formData.id = response.newId
                  const newItem = { ...formData }
                  items.value.push(newItem)
                  flashMessage.value = `${capitalize(titleSingular.value)} ${newItem[name_field.value]} added successfully.`
                } else {
                  const selectedItem = items.value[selectedIndex.value]
                  Object.assign(selectedItem, formData)
                  flashMessage.value = 'Changes saved successfully.'
                }
      
                // Object.assign( formData, {})
                for (let key in formData) {delete formData[key]}
                flashMessageVariant.value = 'info'
                editing.value = adding.value = false
                selectedIndex.value = -1
                formErrors.value = []
              }
            } catch (error) {
              console.log('Error in onSubmitForm:', error)
            }
          }

          const deleteItem = async (id, event) => {
              try {
                  const url = `${props.apiDeleteEndpoint}?id=${id}`
  
                  const response = await axiosPost(url);
                  if (response.result === 'failed') {
                      flashMessageVariant.value = 'warning'
                      flashMessage.value = response.message
                  } else {
                      const name = formData[name_field.value]
                      items.value.splice(selectedIndex.value, 1)
                      flashMessageVariant.value = 'info'
                      flashMessage.value = `${capitalize(titleSingular.value)} ${name} deleted successfully.`
                      editing.value = adding.value = false
                  }
  
              } catch(error) {
                  console.log(error)
                  if (error.response && error.response.status == 400) {
                      flashMessage.value = 'Session expired. Please refresh page.'
                  } else {
                      console.log('Error in deleteItem:', error);
                  }
              }
          }

        return { editing, adding, selected, selectedName, formData, formErrors,
            flashMessage, flashMessageVariant, fields, items, sortState, title, name_field, fieldsOrder, 
            currentPage, perPageOptions, perPage, totalRows, titleSingular, titlePlural,
            onHeaderClick, onClickSortBadge, onClickRow, onClickAdd, onClickCloseAlert, 
            undoEdit, saveEdit, submitForm, deleteItem,
            pluralize, onPageChanged, onSearchChanged,
             }
    },
    delimiters: ['[[',']]'],
    template: templateCache.value,
}

export default VueTable