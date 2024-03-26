<template>
    <div class="chat-history-item">
      <div class="item-header">
        <div class="subject">{{ subject }}</div>
        <div class="date">{{ formattedDate }}</div>
      </div>
      <div class="item-body">
        <div class="from">From: {{ from }}</div>
        <div class="preview-message">"{{ truncatedMessage }}"</div>
      </div>
    </div>
  </template>

<script lang="ts">
import { computed, defineComponent, PropType } from 'vue';

export default defineComponent({
    props: {
        id: String,
        subject: {
            type: String,
            required: true,
        },
        creationDate: {
            type: String, // Assuming ISO string for simplicity; adjust as needed
            required: true,
        },
        from: {
            type: String,
            required: true,
        },
        latestMessage: {
            type: String,
            required: true,
        },
    },
    setup(props) {
        const truncatedMessage = computed(() => props.latestMessage.slice(0, 100) + (props.latestMessage.length > 100 ? "..." : ""));
        const formattedDate = computed(() => {
            // Example date formatting; adjust as needed
            const date = new Date(props.creationDate);
            return date.toLocaleDateString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric'
            });
        });

        return {
            truncatedMessage,
            formattedDate
        }

    }
})
</script>

<style scoped>
.chat-history-item {
  display: flex;
  flex-direction: column;
  padding: 10px;
  border-bottom: 1px solid #eaeaea;
  cursor: pointer;
  transition: background-color 0.3s;
}

.chat-history-item:hover {
  background-color: #f5f5f5;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.subject {
  font-weight: bold;
}

.date {
  font-size: 0.8rem;
  color: #999;
}

.item-body {
  font-size: 0.9rem;
}

.from {
  color: #333;
  margin-bottom: 4px;
}

.preview-message {
  color: #666;
}
</style>