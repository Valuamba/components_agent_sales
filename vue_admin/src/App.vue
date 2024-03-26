<template>
  <div class="app-container">
    <aside class="history-panel-container">
      <HistoryPanel />
    </aside>
    <section class="conversation-panel-container">
      <ConversationPanelV2 />
      <!-- <ConversationPanel /> -->
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import HistoryPanel from './components/HistoryPanel/HistoryPanel.vue';
import ConversationPanel from './components/ConversationPanel/ConversationPanel.vue';
import ConversationPanelV2 from './components/ConversationPanel/ConversationPanelV2.vue';


export default defineComponent({
  components: {
    HistoryPanel,
    ConversationPanel,
    ConversationPanelV2
  },
});
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%; /* Ensure the body takes the full height of the viewport */
}

*, *::before, *::after {
  box-sizing: border-box;
}

.app-container {
  display: flex;
  justify-content: stretch; /* Ensure children stretch to fill the container */
  align-items: stretch; /* Align items vertically */
  width: 100%;
  height: 100vh; /* Set the container to take up the full viewport height */
}

.history-panel-container {
  width: 30%; /* Adjusted width to 30% */
  border-right: 1px solid #ccc;
  overflow-y: auto;
  flex-shrink: 0; /* Prevent the container from shrinking */
  /* Removed height: 100%; since it's already implied by parent's align-items: stretch */
}

.conversation-panel-container {
  flex-grow: 1; /* Allow this container to grow and fill the available space */
  overflow-y: auto; /* Enable scrolling if content overflows */
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%; /* Ensure it takes up all the width of its parent */
  color: #555;
  font-size: 1.5rem;
}

</style>
