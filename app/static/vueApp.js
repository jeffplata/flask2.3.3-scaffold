import DataTable from './dataTable.js';

Vue.component('data-table', DataTable)

Vue.use(BootstrapVue);

// create Vue app
const app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
  })
  
  // make it global
  window.app = app