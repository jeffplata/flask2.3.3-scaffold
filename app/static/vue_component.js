import VuePagination from '/static/vuePagination.js'
import VueTable from '/static/vueTable.js'
import VueSearchInput from '/static/vueSearchInput.js'
import VueTagEditor from '/static/VueTagEditor.js'
const app = Vue.createApp({
  setup() {
    // ...
  },
  delimeters: ['[[', ']]']
  })
  
  app.component('VueTagEditor', VueTagEditor)
  app.component('VueSearchInput', VueSearchInput)
  app.component('VuePagination', VuePagination)
  app.component('VueTable', VueTable)
  
  const vm = app.mount('#app')

  export default vm;