#include <mutex>
#include <queue>

#ifndef _ATOMICQUEUE_INCLUDED_
#define _ATOMICQUEUE_INCLUDED_

// threadsafe queue
template<typename T>
class atomic_queue{
	public:
		atomic_queue() : basic_queue{}{};
		void push(const T& val){
			std::lock_guard<std::mutex> lock(mutex);
			basic_queue.push(val);
		}
		void pop(){
			std::lock_guard<std::mutex> lock(mutex);
			basic_queue.pop();
		}
		T& front(){
			std::lock_guard<std::mutex> lock(mutex);
			return basic_queue.front();
		}
		bool empty(){
			std::lock_guard<std::mutex> lock(mutex);
			return basic_queue.empty();
		}
		size_t size(){
			std::lock_guard<std::mutex> lock(mutex);
			return basic_queue.size();
		}
	private:
		std::queue<T> basic_queue;
		std::mutex mutex;
};


#endif
