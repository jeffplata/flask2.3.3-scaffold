// import dataTableTemplate from './dataTable.html'
// let dataTableTemplate = await (await fetch('./static/dataTable.html')).text()
import axios from 'axios'

let dataTableTemplate = await fetch('./dataTable.html').then(res => res.text())

const DataTable =  {
    name: 'DataTable',
    template: dataTableTemplate,
    delimiters: ['[[', ']]'],
    props: {
        apiEndpoint: {
            type: String,
            required: true,
        },
        apiInitEndpoint: {
            type: String,
        },
        apiGetEndpoint: {
            type: String,
        },
        apiAddEndpoint: {
            type: String,
        },
        apiEditEndpoint: {
            type: String,
        },
        apiDeleteEndpoint: {
            type: String,
        }
    },
    data: function() { return {
        title: '',
        title_s: '',
        totalRows: 1,
        currentPage: 1,
        perPage: 3,
        perPageOptions: [3,5,10,20,30,50,100],
        fields: [],
        items: [],
        filter: '',
        editing: false,
        adding: false,
        selected: {},
        selectedIndex: -1,
        form: {
            id: -1,
            username: '',
            email: '',
            first_name: '',
            last_name: '',
        },
        formErrors: {},
        flashMessage: '',
        flashMessageVariant: '',
        sortBy: '',
        sortDesc: false,
        confirmDelete: '',
    }},
    watch: {
        flashMessage(newVal) {
            if (newVal == '') {
                this.flashMessageVariant = 'warning'
            }
        },
        filter(newVal, oldVal) {
            if (newVal != oldVal) {
                this.fetchData('filter')
            }
        },
        adding() {
            if (this.adding) {
                this.resetForm()
                this.formErrors = {}
                this.flashMessage = ''
            }
        },
        editing() {
            if (this.editing && !this.adding) {
                //this.form = Object.assign({}, this.selected);
                // same here, making a copy, ES6
                this.form = {...this.selected[0]}
                this.formErrors = {}
                this.flashMessage = ''
            }
        },
        perPage(newVal, oldVal) {
            if (typeof oldVal != 'undefined') {
                this.currentPage = 1
                this.fetchData('page')
                localStorage.setItem('perPage', JSON.stringify(newVal));
            }
        },
    },
    
    filters: {
        capitalize: function (data) {
            var capitalized = []
            data.split(' ').forEach(word => {
                capitalized.push(
                    word.charAt(0).toUpperCase() +
                    word.slice(1).toLowerCase()
                )
            })
            return capitalized.join(' ')
        },
        pluralize: function(amount, singular, plural) {
            return amount > 1 || amount === 0 ? plural : singular
        }
    },
    computed: {
        isFormErrors() {
            return Object.entries(this.formErrors).length > 0
        }
    },
    methods: {
        async showMsgBoxConfirm() {
            this.confirmDelete = ''
            this.$bvModal.msgBoxConfirm('Please confirm that you want to delete this record.', {
              title: 'Please Confirm',
              size: 'sm',
              buttonSize: 'sm',
              okVariant: 'danger',
              okTitle: 'YES',
              cancelTitle: 'NO',
              footerClass: 'p-2',
              hideHeaderClose: false,
              opacity: 0.6,
              centered: true
            })
              .then(value => {
                this.confirmDelete = value
                if (value) {
                    this.onDeleteRow()
                }
              })
              .catch(err => {
                console.log(err)
              })
          },
        onSortChanged(ctx) {
            this.sortBy = ctx.sortBy
            this.sortDesc = ctx.sortDesc
            this.fetchData('sort')
        },
        onRowClicked(item, index) {
            this.selectedIndex = index
        },
        resetForm() {
            this.form.id = -1
            this.form.username = ''
            this.form.email = ''
            this.form.first_name = ''
            this.form.last_name = ''
            this.formErrors = {}
        },
        async axiosPost(url, data) {
            try {
                const response = await axios.post(url, data, {
                    headers: { 'Content-Type': 'application/json' },
                });
                return response.data;
            } catch (error) {
                console.error('Axios Error:', error);
                throw error;
            }
        },
        async onDeleteRow() {
            try {
                const id = this.selected[0].id;
                const url = this.apiEndpoint + 'user_delete' + `?id=${id}`
                this.flashMessage = '';

                const response = await this.axiosPost(url);
                if (response.result === 'failed') {
                    this.flashMessage = response.message
                } else {
                    const username = this.items[this.selectedIndex].username
                    this.items.splice(this.selectedIndex, 1)
                    this.flashMessage = `User ${username} deleted successfully.`
                    this.flashMessageVariant = 'info'
                }

            } catch(error) {
                if (error.response.status == 400) {
                    this.flashMessage = 'Session expired. Please refresh page.'
                } else {
                    console.log('Error in onDeleteRow:', error);
                }
            }
        },

        async onSubmitForm() {
            try {
                const url = this.apiEndpoint + this.apiEditEndpoint;
                const bodyFormData = new FormData();
                for (const [key, value] of Object.entries(this.form)) {
                    bodyFormData.append(key, value);
                }

                const response = await this.axiosPost(url, bodyFormData);
                if (response.message) {
                    this.flashMessage = response.message
                }
                if (response.result === 'failed') {
                    this.formErrors = response.errors;
                } else {
                    if (this.adding) {
                        let username = this.form.username
                        this.form.id = response.newId
                        const newItem = { ...this.form }
                        this.items.push(newItem)
                        this.flashMessage = `User ${username} added successfully.`
                    } else {
                        const selectedItem = this.items[this.selectedIndex]
                        Object.assign(selectedItem, this.form)
                        this.flashMessage = `Changes saved successfully.`
                    }
                    this.flashMessageVariant = 'info'
                    this.editing = this.adding = false
                }

            } catch(error) {
                // if (error.response.status == 400) {
                //     this.flashMessage = 'Session expired. Please refresh page.'
                // } else {
                    console.log('Error in onSubmitForm:', error)
                // }
            }
        },

        onPageChange(page) {
            this.currentPage = page
            this.fetchData('page')
        },
        onRowSelected(items) {
            this.selected = items;
        },
        onFiltered(filteredItems) {
            this.totalRows = filteredItems.length
            this.currentPage = 1
        },
        fetchData(triggeredBy = '') {
            var endPoint = this.apiEndpoint + this.apiGetEndpoint
            var startIndex = (this.currentPage - 1) * this.perPage;
            var sortArgs = ''
            var filterArgs = ''
            if (triggeredBy in ['filter', 'sort']) {
                startIndex = 0
            }
            const pageArgs = `?start=${startIndex}&limit=${this.perPage}`
            filterArgs = `&filtertext=${this.filter}`
            sortArgs = `&sortby=${this.sortBy}&sortdesc=${this.sortDesc}`
            // var debug_args = `&debug=${triggeredBy}`
            axios
                .get(endPoint + pageArgs + filterArgs + sortArgs /* + debug_args */)
                .then(response => {
                    const data = response.data
                    this.items = data.data
                    this.fields = data.fieldnames
                    this.totalRows = data.totalrows
                    if (triggeredBy in ['filter', 'sort']) {
                        this.currentPage = 1
                    }
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                })

            this.flashMessage = '';
        },
    },

    created: async function(){
        const gResponse = await fetch(this.apiEndpoint + this.apiInitEndpoint);
        const gObject = await gResponse.json();
        let title = gObject.title.split('|')
        this.title_s = title[0];
        this.title = title.length > 1 ? title[1] : title[0]
    },
    mounted() {
        let optionN = this.perPageOptions
        this.perPageOptions = optionN.map(n => ({'value': n, 'text': `${n} items`}))
        this.perPage = JSON.parse(localStorage.getItem('perPage')) || 10
        // this.fetchData() #  fetch due to currentPage change is triggered on load
    }

}

export default DataTable