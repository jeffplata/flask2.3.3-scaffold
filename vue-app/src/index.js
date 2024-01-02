import DataTable from './components/dataTable.vue' 

// Import child components
import TableBare from './components/tableBare.vue'
import PaginationBare from './components/paginationBare.vue'

// Install function 
const install = (app) => {

  app.component('DataTable', DataTable)  

  // Register child components
  app.component('TableBare', TableBare)
  app.component('PaginationBare', PaginationBare)

}

// Create plugin object
export default {
  install,
  DataTable,
  TableBare,
  PaginationBare
}



// ===============
// import { createApp } from 'vue'

// import 'bootstrap/dist/css/bootstrap.css';
// import 'bootstrap/dist/js/bootstrap.js';

// import "../src/assets/fontawesome/css/fontawesome.css";
// import "../src/assets/fontawesome/css/brands.css";
// import "../src/assets/fontawesome/css/solid.css";

// import DataTable from "./components/dataTable.vue";
// import TableBare from "./components/dataTable.vue";
// import PaginationBare from "./components/dataTable.vue";

// const app = createApp(DataTable)
// app.component('table-bare', TableBare)
// app.component('pagination-bare', PaginationBare)

// export {DataTable, TableBare, PaginationBare};


// ======================
// import { createApp } from 'vue';
// import DataTable from './DataTable.vue';

// Optionally, register any globally used child components here
// import ChildComponent1 from './ChildComponent1.vue';
// import ChildComponent2 from './ChildComponent2.vue';
// createApp().component('child-component-1', ChildComponent1);
// createApp().component('child-component-2', ChildComponent2);

// const app = createApp(DataTable);

// Optionally, mount the app to a specific element if needed
// app.mount('#app');

// Export the app instance for UMD usage
// export default app;