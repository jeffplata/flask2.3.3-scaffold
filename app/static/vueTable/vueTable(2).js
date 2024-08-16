import { changeSort, formatColumnTitle, pluralize, capitalize, addStyles } from './vueTableUtils.js';

const { ref, reactive, computed, watch, onMounted } = Vue;

const templateCache = ref(null)
if (!templateCache.value) {
    const response = await fetch('./static/vuetable/vueTable.html')
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
            align-items: center;
        }

        .header-clickable {
            cursor: pointer;
        }

        form label {
            font-weight: 600;
        }
`
// // Function to add styles to the head of the document
// const addStyles = (styles) => {
//     const styleElement = document.createElement('style');
//     styleElement.textContent = styles;
//     document.head.appendChild(styleElement);
// };

addStyles(styles); // Adding styles to the head

const VueTable = {
    props: ['apiEndpoint'],
    emits: ['pageChanged', 'searchChanged'],
    setup(props) {
        const apiEndpointValue = props.apiEndpoint
        const editing = ref(false)
        const adding = ref(false)
        const selected = ref([])
        const selectedIndex = ref(-1)
        const flashMessage = ref('Loading...')
        const flashMessageVariant = ref('info')
        const currentPage = ref(1)
        const perPage = ref(0)
        const perPageOptions = ref([3,5,10,20,30,50,100])
        const totalRows = ref(0)
        const filter = ref('')
        const fields = ref([])
        const links = ref([])
        // const linkParentId = ref(-1)
        const linkShowingTitle = ref('')
        const items = ref([])
        const items_display = ref([])
        const formData = reactive({})  // use Object.assign not formData.value = ...
        const undoData = reactive({})
        const formErrors = ref([])

        const entity = apiEndpointValue.split('/')[1]
        const title = ref('')
        const name_field = ref('')
        const fieldsOrder = ref([])

        // const selectedName = computed(() => {
        //     return this.selected.value.length > 0 ? this.selected.value[0].name : '';
        // })

        const titleSingular = computed(() => {return pluralize(1, title.value)})
        const titlePlural = computed(() => {return pluralize(2, title.value)})

        const sortState = ref({
            key: '',
            descending: true  
          })

        const initialPerPage = 10
        const linkTable = reactive({
          items: [],
          key: '',
          parentId: -1,
          totalRows: 0,
          currentPage: 1,
          perPage: initialPerPage,
          perPageOptions: [
            {'value': 5, 'text': '5 items'},
            {'value': 10, 'text': '10 items'},
            {'value': 25, 'text': '25 items'},
            {'value': 100, 'text': '100 items'},
          ],
          start: 1,
          limit: initialPerPage,
          placeholder: '',
          lookupUrl: '',

          onItemSelected: async (itemId) => {
            linkTable.addItem(itemId)
          },
          onClickDelete: (itemId, itemIndex) => {
            linkTable.deleteItem(linkTable.parentId, itemId, itemIndex)
          },
          onClickLink: (itemindex, id, key, record_name) => {
            selectedIndex.value = itemindex
            linkTable.parentId = id
            linkTable.key = key
            linkShowingTitle.value = `${key} of ${titleSingular.value} '${record_name}'`
            for (const item of links.value) {
              if (item.key === key) {
                linkTable.totalRows = item.totalRows[itemindex]
                linkTable.lookupUrl = item.link
                linkTable.placeholder = item && item.placeholder ? 
                  item.placeholder : 'Select an item to add...'
              }
            }
            flashMessage.value = ''

            // const linkItem = links.value.find((el) => el.key === linkTable.key)
            // linkTable.placeholder = linkItem && linkItem.placeholder ? 
            //   linkItem.placeholder : 'Select an item to add...'
          },
          onPageChanged: (page) => {
            linkTable.currentPage = page
            linkTable.start = 1
            linkTable.limit = linkTable.perPage
            flashMessage.value = ''
          },
          getLinkByKey: (key) => {
            for (const el of links.value) {
              if (el.key === key) {
                return el;
              }
            }
            return None;
          },
          columnTitles: (key) => {
            const linkItem = linkTable.getLinkByKey(key)
            return linkItem.fields ? linkItem.fields : ['No titles found!']
          },
          fetch: async () => {
            const key = linkTable.key
            // const id = linkTable.parentId
            const linkItem = linkTable.getLinkByKey(key)
            const endPoint = linkItem.link + `/get/${linkTable.parentId}`
            const start = (linkTable.currentPage - 1) * linkTable.perPage
            const limit = linkTable.limit
            const fields = linkTable.getLinkByKey(key).fields.join(',')
            try {
              const response = await axios.get(`${endPoint}?start=${start}&limit=${limit}&fields=${fields}`)
              const data = response.data
              // linkTable.items = data.data
              linkTable.totalRows = data.totalRows
              items.value[selectedIndex.value][linkTable.key] = data.data
            } catch (error) {
              console.log('Error in linkTable fetch:', error)
            }
          },
          addItem: async(childId) => {
            try {
              const linkItem = linkTable.getLinkByKey(linkTable.key)
              const linkFields = linkItem.fields
              const endPoint = linkItem.link + `/new/${linkTable.parentId}?id=${childId}&linkFields=${linkFields}`
              const response = await axios.post(`${endPoint}`)
              const resp = response.data
              if (resp.result == 'ok') {
                // const newData = resp.data
                items.value[selectedIndex.value][linkTable.key].push(resp.data)
                linkItem.totalRows[selectedIndex.value] = Number(linkItem.totalRows[selectedIndex.value]) + 1
                linkTable.totalRows = Number(linkTable.totalRows) + 1
              } else {
                flashMessageVariant.value = 'warning'
                flashMessage.value = resp.message      
              }
            } catch (error) {
              console.log('Error in onItemSelected:', error)
            }
          },
          deleteItem: async (parentId, childId, itemIndex) => {
            const linkItem = linkTable.getLinkByKey(linkTable.key)
            const endPoint = linkItem.link + `/delete/${parentId}?id=${childId}`
            try {
              const response = await axios.post(`${endPoint}`)
              const resp = response.data
              if (resp.result == 'ok') {
                items.value[selectedIndex.value][linkTable.key].splice(itemIndex, 1)
                linkItem.totalRows[selectedIndex.value] = Number(linkItem.totalRows[selectedIndex.value]) - 1
                linkTable.totalRows = Number(linkTable.totalRows) - 1
                flashMessageVariant.value = 'info'
                flashMessage.value = resp.message || 'Item successfuly deleted.'
              } else {
                flashMessageVariant.value = 'warning'
                flashMessage.value = resp.message      
              }
            } catch (error) {
              console.log('Error in linkTable delete:', error)
            }
          }
        })


        onMounted(() => {
            let optionN = perPageOptions.value
            perPageOptions.value = optionN.map(n => ({'value': n, 'text': `${n} items`}))
            perPage.value = JSON.parse(localStorage.getItem('perPage')) || 10

            // const linkItem = links.value.find((el) => el.key === linkTable.key)
            // linkTable.placeholder = linkItem ? linkItem.place : 'Select an item to add...'
        })

        const isColumnVisible = (columnTitle) => {
            if (!columnTitle) {return undefined}
            let col = fields.value.find(item => item.key === columnTitle.key)
            return !col.hasOwnProperty('visible') || col.visible
        }

        const getColumnDisplay = (field, value) => {
          if (items_display.value.hasOwnProperty(field)) {
            return items_display.value[field](value);
          } else {
            return value
          }
        }

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
              if (data['display']) {
                for (const [key, funcString] of Object.entries(data.display)) {
                  try {
                    const lambdaFunction = new Function('return ' + funcString)();
                    items_display.value[key] = lambdaFunction;
                  } catch (error) {
                    console.error('Error converting function for key ${key}:', error)
                  }
                }
              }

              fields.value = data.fieldnames
              links.value = data.links
              totalRows.value = data.totalrows
              flashMessage.value = ''

              fieldsOrder.value = []
              fields.value.forEach((el, index) => {
                fieldsOrder.value.push(typeof el!=='string' ? el.key : el)
                if (typeof el!=='string') {
                    el.title = formatColumnTitle(el.key)
                    el.sortdesc = false
                } else {
                    fields.value[index] = {key: el, title: formatColumnTitle(el), 
                      sortable: 'false',sortdesc: false
                    }
                }
              });
      
              // get init data title and name_field
              try {
                // const response = await axios.get(apiEndpointValue+'_init')
                const response = await axios.get(`${props.apiEndpoint}/init`)
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

        watch(() => linkTable.currentPage, () => {
          linkTable.fetch();  })
        watch(() => linkTable.perPage, (nv, ov) => { 
          flashMessage.value = ''
          linkTable.limit = nv
          if (linkTable.currentPage !== 1) {
            linkTable.currentPage = 1
          } else {
            linkTable.fetch(); 
            }
          })

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
          if (!adding.value) {
            items.value.splice(selectedIndex.value, 1, structuredClone(_.cloneDeep(undoData)))
          }
          selectedIndex.value = -1
          adding.value = editing.value = false
        }

        function onClickCloseAlert() {
            flashMessage.value = ''
        }

        // function onClickLink(itemindex, id, key, record_name) {
        //   console.log(itemindex,id,key,record_name)
        //   selectedIndex.value = itemindex
        //   linkParentId.value = id
        //   linkShowingTitle.value = `${key} of ${titleSingular.value} '${record_name}'`
        // }

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
              // const url = `${props.apiEditEndpoint}`
              let url = ''
              if (adding.value) { 
                formData.id = -1
                url = `${props.apiEndpoint}/new`
              } else {
                url = `${props.apiEndpoint}/edit/${formData.id}`
              }
              // const url = `${props.apiEndpoint}`
              const bodyFormData = new FormData()
              let tempFormData = new FormData()

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

              // convertArraysToJSON ensures that arrays and objects in the items
              //    are properly serialized as JSON objects; useful for master-detail
              //    scenarios
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
                  // const newItem = { ...formData }
                  const newItem = _.cloneDeep(response.data)
                  items.value.push(newItem)
                  totalRows.value = Number(totalRows.value) + 1
                  flashMessage.value = `${capitalize(titleSingular.value)} ${newItem[name_field.value]} added successfully.`
                } else {
                  const selectedItem = items.value[selectedIndex.value]
                  // Object.assign(selectedItem, formData)
                  const editedData = _.cloneDeep(response.data)
                  Object.assign(selectedItem, editedData)
                  flashMessage.value = `Changes to ${titleSingular.value} ${editedData[name_field.value]} saved successfully.`
                }
      
                // Object.assign( formData, {})
                // The correct way to initialize an object is to delete all keys
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
                  // const url = `${props.apiDeleteEndpoint}?id=${id}`
                  const url = `${props.apiEndpoint}/delete/${id}`
  
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
                  if (error.response && error.response.status == 400) {
                      flashMessage.value = 'Session expired. Please refresh page.'
                  } else {
                      console.log('Error in deleteItem:', error);
                  }
              }
          }

        return { editing, adding, selected, selectedIndex, formData, formErrors,
            flashMessage, flashMessageVariant, fields, links, 
            linkShowingTitle, linkTable, items, sortState, title, name_field, 
            fieldsOrder, currentPage, perPageOptions, perPage, totalRows, titleSingular, titlePlural,
            items_display, capitalize, columnVisible: isColumnVisible,
            onHeaderClick, onClickSortBadge, onClickRow, onClickAdd, onClickCloseAlert, 
            undoEdit, saveEdit, submitForm, deleteItem,
            pluralize, onPageChanged, onSearchChanged, getColumnDisplay,
            // onClickLink,
            // selectedName,
             }
    },
    delimiters: ['[[',']]'],
    template: templateCache.value,
}

export default VueTable