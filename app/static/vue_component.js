import VuePagination from '/static/vuePagination.js'
import VueTable from '/static/vueTable.js'
const app = Vue.createApp({
    setup() {
      // ...
    }
  })
  
  app.component('VueTable', VueTable)
  app.component('VuePagination', VuePagination)
  
  app.mount('#app')