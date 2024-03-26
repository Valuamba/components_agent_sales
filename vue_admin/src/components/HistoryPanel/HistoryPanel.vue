
<template>
    <div class="history-panel">
      <div class="title">Chat History</div>
      <div class="history-list">
        <ChatHistoryItem
          v-for="item in chatHistory"
          :key="item.id"
          :subject="item.subject"
          :creationDate="item.creationDate"
          :from="item.from"
          :latestMessage="item.latestMessage"
        />
      </div>
    </div>
  </template>

<script lang="ts">

import { defineComponent } from 'vue';
import ChatHistoryItem from './ChatHistoryItem.vue';
import { useStore } from 'vuex';

export default defineComponent({
    components: {
        ChatHistoryItem,
    },
    // setup() {
    //     // const store = useStore();

    //     const chatHistory = [
    //         {
    //             id: 12, 
    //             name: "kek",
    //             lastMessage: "kokos"
    //         }
    //     ];

    //     return {
    //         chatHistory
    //     }
    // },
    data() {
        return {
        // Mock data for chat history
        chatHistory: [
            {
            id: '1',
            subject: 'Order Inquiry',
            creationDate: '2023-03-24T14:22:00.000Z',
            from: 'Customer A',
            latestMessage: 'Hello, I would like to inquire about the status of my order placed last week. I have not yet received a shipping confirmation.',
            },
            {
            id: '2',
            subject: 'Product Feedback',
            creationDate: '2023-03-23T11:30:00.000Z',
            from: 'Customer B',
            latestMessage: 'I recently purchased your product and have some feedback I would like to share. I noticed that...',
            },
            // Add more items as needed
        ],
        };
  },
})

</script>

<style scoped>
.history-panel {
  padding: 10px;
}

.title {
  font-size: 1.2em;
  margin-bottom: 10px;
}

.history-list {
  max-height: 500px;
  overflow-y: auto;
}
</style>