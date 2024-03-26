<template>
    <div>
      <div class="message-item" :class="{'customer-message': message.sender === 'customer', 'my-message': message.sender !== 'customer'}">
        <div class="message-header">
          <span class="sender-name">{{ message.sender === 'customer' ? 'Customer' : 'Me' }}</span>
          <span class="message-date">{{ formattedDate }}</span>
        </div>
        <div class="message-text">{{ message.text }}</div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, PropType, computed } from 'vue';
  
  export default defineComponent({
    props: {
      message: {
        type: Object as PropType<{ id: string; text: string; sender: string, date: string }>, // Adjust the type as necessary
        required: true,
      },
    },
    setup(props) {
      // Format the message date for display
      const formattedDate = computed(() => {
        const date = new Date(props.message.date);
        if (isNaN(date.getTime())) {
          // Handle invalid dates gracefully
          return "Date unavailable";
        }
        return date.toLocaleString(undefined, {
          day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
      });
  
      return {
        formattedDate,
      };
    },
  });
  </script>
  
  <style scoped>
  .message-item {
    display: flex;
    flex-direction: column;
    margin: 10px;
    padding: 10px;
    border-radius: 8px;
    max-width: 80%;
  }
  
  .customer-message {
    align-self: flex-start;
    background-color: LightGreen; /* Customer messages in LightGreen */
  }
  
  .my-message {
    align-self: flex-end;
    background-color: LightGray; /* Your messages in LightGray */
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
  }
  
  .sender-name {
    font-weight: bold;
  }
  
  .message-date {
    font-size: 0.8rem;
    color: #666;
  }
  
  .helpful-instructions {
    margin-top: 10px;
    align-self: flex-end;
  }
  </style>
  