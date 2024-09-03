import VuePagination from '/static/vueTable/vuePagination.js'
import VueTable from '/static/vueTable/vueTable.js'
import VueSearchInput from '/static/vueTable/vueSearchInput.js'
import VueTagEditor from '/static/vueTable/vueTagEditor.js'
import VueAddItemPanel from '/static/vueTable/vueAddItemPanel.js'
import VueLinkTable from '/static/vueTable/vueLinkTable.js'
import VueSelectField from '/static/vueTable/vueSelectField.js'
const app = Vue.createApp({
  setup() {
    // ...
  },
  delimeters: ['[[', ']]']
  })
  
  app.component('VueSelectField', VueSelectField)
  app.component('VueAddItemPanel', VueAddItemPanel)
  app.component('VueLinkTable', VueLinkTable)
  app.component('VueTagEditor', VueTagEditor)
  app.component('VueSearchInput', VueSearchInput)
  app.component('VuePagination', VuePagination)
  app.component('VueTable', VueTable)
  
  const vm = app.mount('#app')

  export default vm;