import { useCapitalize } from "./stringUtils.js";
import { changeSort } from './vueTableUtils.js';

const { ref, computed } = Vue;

const templateCache = ref(null)
if (!templateCache.value) {
    const response = await fetch('./static/vueTable.html')
    const templateText = await response.text()

    templateCache.value = templateText
}

const VueTable = {
    props: ['fm'],
    setup() {
        const editing = ref(false)
        const adding = ref(false)
        const selected = ref([])
        const flashMessage = ref('Welcome to VueTable.')
        const fields = ref(['id', {key: 'name', sortable: true}, {key: 'age', sortable: true}])
        const items = ref(
            [{id: 0, name: 'Bob', age: 45},
            {id: 1, name: 'Alfred', age: 76},
            {id: 3, name: 'Sinclair', age: 15},
            {id: 4, name: 'Gandalf', age: 138},
            {id: 5, name: 'Randolph', age: 12}]
        )

        const sortState = ref({
            key: '',
            descending: true  
          })

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

        function onClickRow(row) {
            flashMessage.value = row
            editing.value = true
            selected.value = [row]
        }

        function onClickCloseAlert() {
            flashMessage.value = ''
        }

        return { editing, adding, selected, selectedName,
            flashMessage, fields, items, sortState,
            onHeaderClick, onClickSortBadge, onClickRow, onClickCloseAlert,
             }
    },
    delimiters: ['[[',']]'],
    template: templateCache.value,
}

export default VueTable