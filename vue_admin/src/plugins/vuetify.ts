// src/plugins/vuetify.js

// Import Vuetify
import { createVuetify } from 'vuetify';
import 'vuetify/styles'; // Ensure you're importing Vuetify styles

// Import any Vuetify components you plan to use
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

// Create the Vuetify instance
export default createVuetify({
  components,
  directives,
  // any additional options
});
