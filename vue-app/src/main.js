import { createApp } from 'vue'

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';
// import "../node_modules/bootswatch/dist/flatly/bootstrap.min.css";

import "../src/assets/fontawesome/css/fontawesome.css";
import "../src/assets/fontawesome/css/brands.css";
import "../src/assets/fontawesome/css/solid.css";

import App from './App.vue'
// import router from './router'

const app = createApp(App);

// app.use(router);

app.mount("#app");
