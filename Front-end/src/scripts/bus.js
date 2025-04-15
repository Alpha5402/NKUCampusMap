// bus.js
import mitt from 'mitt'; // 使用 mitt 库实现事件总线

const EventBus = mitt(); // 创建一个事件总线实例

export { EventBus };
