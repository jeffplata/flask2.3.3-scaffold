import { changeSort, capitalize, pluralize } from './vueTableUtils.js';
// import VuePagination from './vuePagination.js';

const { ref, computed, watch, onMounted } = Vue;

const templateCache = ref(null)
if (!templateCache.value) {
    const response = await fetch('./static/vueTable.html')
    const templateText = await response.text()

    templateCache.value = templateText
}

const styles = `
        .sort-off {
            color: lightgray
        }
    
        .sort-badge {
            cursor: pointer;
            float: right;
        }

        form label {
            font-weight: 500;
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
    props: ['apiEndpoint'],
    emits: ['pageChanged'],
    setup(props) {
        const apiEndpointValue = props.apiEndpoint
        const editing = ref(false)
        const adding = ref(false)
        const selected = ref([])
        const flashMessage = ref('Welcome to VueTable.')
        const currentPage = ref(1)
        const perPage = ref(3)
        const perPageOptions = ref([3,5,10,20,30,50,100])
        const totalRows = ref(0)
        const filter = ref('')
        const fields = ref([])
        const items = ref([])
        const formData = ref(null)

        const entity = apiEndpointValue.split('/')[1]
        const title = ref('')
        const name_field = ref('')
        const fieldsOrder = ref([])

        fields.value.forEach((el, index) => {
            if (typeof el!='string') {
                el.sortdesc = false
                // el.key = useCapitalize(el.key)
            } else {
                // fields.value[index] = useCapitalize(el);
            }
        });

        const selectedName = computed(() => {
            return this.selected.value.length > 0 ? this.selected.value[0].name : '';
        })

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

        watch([currentPage, filter], () => {
            fetchData()
        })

        watch(perPage, () => {fetchData('perPage')})

        function onClickSortBadge() {
            sortState.value = {key: '', descending: false}
        }

        function onHeaderClick(fld) {
            if (typeof fld!=='string') {
                sortState.value = changeSort(
                    sortState.value,
                    fld.key, 
                    fld.key === sortState.value.key ? !sortState.value.descending : false
                  )
            }
        }

        function onClickRow(row, id) {
            editing.value = true
            selected.value = [row]
            formData.value = {...row}
        }

        function saveEdit() {
            adding.value = editing.value = false
            if (formData.value) {
                const itemIndex = items.value.findIndex((i) => i.id === formData.value.id);
                items.value[itemIndex] = { ...formData.value }
                formData.value = null
            }
        }

        function undoEdit() {
            adding.value = editing.value = false
            formData.value = null
        }

        function onClickCloseAlert() {
            flashMessage.value = ''
        }

        function onPageChanged(newPage) {
            currentPage.value = newPage
        }

        return { editing, adding, selected, selectedName, formData,
            flashMessage, fields, items, sortState, title, name_field, fieldsOrder, 
            currentPage, perPageOptions, perPage, totalRows,
            onHeaderClick, onClickSortBadge, onClickRow, onClickCloseAlert, 
            undoEdit, saveEdit,
            pluralize, onPageChanged,
             }
    },
    delimiters: ['[[',']]'],
    template: templateCache.value,
}

export default VueTable