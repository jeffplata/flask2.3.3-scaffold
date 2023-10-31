const apiEndpoint = '/api_v1/';

Vue.use(BootstrapVue);

const vm = new Vue({ // Again, vm is our Vue instance's name for consistency.
    el: '#vm',
    delimiters: ['[[', ']]'],
    data: {
        title: '',
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
        errorMessage: '',
        sortBy: '',
        sortDesc: false,
        confirmDelete: '',
    },
    watch: {
        filter(newVal, oldVal) {
            if (newVal != oldVal) {
                this.fetchData('filter')
            };
        },
        adding() {
            if (this.adding) {
                this.resetForm()
                this.errorMessage = ''
            }
        },
        editing() {
            if (this.editing && !this.adding) {
                //this.form = = Object.assign({}, this.selected);
                // same here, making a copy, ES6
                this.form = {...this.selected[0]}
                this.errorMessage = ''
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
              centered: true
            })
              .then(value => {
                this.confirmDelete = value
                if (value) {
                    this.onDeleteRow()
                }
              })
              .catch(err => {
                // An error occurred
              })
          },
        onSortChanged(ctx) {
            this.sortBy = ctx.sortBy
            this.sortDesc = ctx.sortDesc
            this.fetchData('sort')
        },
        onRowClicked(item, index, event) {
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
        //TODO refactor ondeleterow and onsubmitform as suggested by chatgpt. see example
        onDeleteRow() {
            var vm = this
            var id = vm.selected[0].id
            var url = apiEndpoint + 'user_delete' + `?id=${id}`
            this.errorMessage = ''
            axios({
              method: "post",
              url: url,
              headers: { "Content-Type": "application/json" },
            })
              .then(function (response) {
                if (response.data.result === 'failed') {
                    if (response.data.message === 'record not allowed') {
                        vm.errorMessage = 'You are not allowed to delete this user.'
                    } else {
                        vm.errorMessage = 'Failed to delete.'
                    }
                } else {
                    let username = vm.items[vm.selectedIndex].username
                    vm.items.splice(vm.selectedIndex, 1)
                    vm.errorMessage = `User ${username} deleted successfully.`
                }
              })
              .catch(function (response) {
                console.log(response)
              });
        },
        onSubmitForm(event) {
            let vm = this;
            var url = apiEndpoint + 'user_add';
            var bodyFormData = new FormData();
            for (var key in vm.form) {
              if (vm.form.hasOwnProperty(key)) {
                bodyFormData.append(key, vm.form[key]);
              }
            };
            axios({
              method: "post",
              url: url,
              data: bodyFormData,
              headers: { "Content-Type": "application/json" },
            })
              .then(function (response) {
                if (response.data.message === 'failed') {
                    vm.formErrors = response.data.errors;
                } else {
                    if (vm.adding) {
                        vm.form.id = response.data.newId
                        // let {id, username, email, first_name, last_name} = vm.form
                        // let newItem = {id, username, email, first_name, last_name}
                        let newItem = {}
                        Object.assign(newItem, vm.form)
                        vm.items.push(newItem)
                        vm.editing = vm.adding = false
                    } else {
                        const selectedItem = vm.items[vm.selectedIndex]
                        Object.assign(selectedItem, vm.form)
                        vm.editing = vm.adding = false
                    }
                };

              })
              .catch(function (response) {
                console.log(response);
              });
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
            var startIndex = (this.currentPage - 1) * this.perPage;
            var sortArgs = ''
            var filterArgs = ''
            if (triggeredBy in ['filter', 'sort']) {
                startIndex = 0
            }
            var pageArgs = `?start=${startIndex}&limit=${this.perPage}`
            filterArgs = `&filtertext=${this.filter}`
            sortArgs = `&sortby=${this.sortBy}&sortdesc=${this.sortDesc}`
            fetch( apiEndpoint + 'users' + pageArgs + filterArgs + sortArgs )
                .then(response => response.json())
                .then(data => {
                  this.items = data.data;
                  this.fields = data.fieldnames;
                  this.totalRows = data.totalrows;
                  if (triggeredBy in ['filter', 'sort']) {
                      this.currentPage = 1
                  }
                })
                .catch(error => {
                  console.error('Error fetching data:', error);
                });
            this.errorMessage = '';
        },

    },

    created: async function(){
        const gResponse = await fetch(apiEndpoint + 'init');
        const gObject = await gResponse.json();
        this.title = gObject.title;
    },
    mounted() {
        let optionN = this.perPageOptions
        this.perPageOptions = optionN.map(n => ({'value': n, 'text': `${n} items`}))
        this.perPage = JSON.parse(localStorage.getItem('perPage')) || 10
        this.fetchData()
    }
})
