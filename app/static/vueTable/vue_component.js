import VuePagination from '/static/vuetable/vuePagination.js'
import VueTable from '/static/vueTable/vueTable.js'
import VueSearchInput from '/static/vuetable/vueSearchInput.js'
import VueTagEditor from '/static/vuetable/VueTagEditor.js'
import VueAddItemPanel from '/static/vuetable/vueAddItemPanel.js'
import VueLinkTable from '/static/vuetable/vueLinkTable.js'
import VueSelectField from '/static/vuetable/vueSelectField.js'
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