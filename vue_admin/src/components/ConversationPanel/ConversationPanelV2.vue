<template>
    <div class="conversation-panel">
      <div class="messages">
        <!-- Directly use MessageItem, which should internally use MsgContent -->
        <MsgContent
          v-for="(msg, index) in messages"
          :key="msg.id"
          :message="msg"
          :index="index"
          :usePrompt="usePrompt"
          :deleteMessage="() => deleteMessage(index)"
        />
      </div>
      <form @submit.prevent="sendMessage">
        <input v-model="newMessage" placeholder="Type a message..." />
        <button type="submit">Send</button>
      </form>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  import MsgContent from './MsgContent.vue'; // Ensure this component is set to use MsgContent internally
  
  export default defineComponent({
    components: {
        MsgContent,
    },
    setup() {
        const messages = [
  {
    id: '1',
    is_bot: true,
    is_disabled: false,
    message: 'Hello! I am your virtual assistant. How can I help you today?'
  },
  {
    id: '2',
    is_bot: false,
    is_disabled: false,
    message: 'I have a question regarding my recent order.'
  },
  {
    id: '3',
    is_bot: true,
    is_disabled: false,
    message: 'Sure, I can help with that. Could you please provide me your order number?'
  },
  {
    id: '4',
    is_bot: false,
    is_disabled: true, // This message could represent a deleted or retracted message.
    message: 'I found the information I needed. Thanks anyway!'
  }
];

    //   const messages = ref([
    //     { id: '1', text: 'Hello! How are you today?', sender: 'support' },
    //     // More messages as needed
    //   ]);
  
      const newMessage = ref('');
  
      const sendMessage = () => {
        // Logic to send a message
      };
  
      const usePrompt = () => {
        // Placeholder for usePrompt logic
      };
  
      const deleteMessage = (index) => {
        messages.value.splice(index, 1);
      };
  
      return {
        messages,
        newMessage,
        sendMessage,
        usePrompt,
        deleteMessage,
      };
    },
  });
  </script>
  
<style>

/* .messages {
    margin: 10px
} */
</style>