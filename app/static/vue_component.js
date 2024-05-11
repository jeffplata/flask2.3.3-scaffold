import VuePagination from '/static/vuePagination.js'
import VueTable from '/static/vueTable.js'
import VueSearchInput from '/static/vueSearchInput.js'
const app = Vue.createApp({
    delimeters: ['[[', ']]'],
    setup() {
      // ...
    }
  })
  
  app.component('VueSearchInput', VueSearchInput)
  app.component('VuePagination', VuePagination)
  app.component('VueTable', VueTable)
  
  app.mount('#app')