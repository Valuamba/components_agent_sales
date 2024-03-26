<template>
    <div class="conversation-panel">
      <div class="messages">
        <MessageItem
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
        />
      </div>
      <form @submit.prevent="sendMessage">
        <input v-model="newMessage" placeholder="Type a message..." />
        <button type="submit">Send</button>
      </form>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, computed, ref } from 'vue';
  import { useStore } from 'vuex';
  import MessageItem from './MessageItem.vue';
  
  export default defineComponent({
    components: {
      MessageItem,
    },
    setup() {
      const store = useStore();
      const newMessage = ref('');
    // Define mock messages directly in component
      const messages = ref([
        { id: '1', text: 'Hello! How can I help you today?', sender: 'support' },
        { id: '2', text: 'I have a question about my order.', sender: 'customer' },
        { id: '3', text: 'Sure, I can help with that. What\'s your order number?', sender: 'support' },
        // Add more messages as needed
    ]);
  
      const sendMessage = () => {
        if (newMessage.value.trim()) {
          // Here you would dispatch an action to send the message
          // For now, just log the message
          console.log("Sending message:", newMessage.value);
          newMessage.value = ''; // Reset input after sending
        }
      };
  
      return {
        messages,
        newMessage,
        sendMessage,
      };
    },
  });
  </script>
  
  <style scoped>
  .conversation-panel {
    display: flex;
    flex-direction: column;
  }
  
  .messages {
    flex: 1;
    overflow-y: auto;
  }
  
  form {
    display: flex;
    margin-top: auto;
  }
  
  input {
    flex: 1;
    margin-right: 10px;
  }
  </style>
  