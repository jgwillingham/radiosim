
#ifndef THREADSAFEQUEUE_INCLUDED
#define THREADSAFEQUEUE_INCLUDED

#include <mutex>
#include <queue>

template<typename T>
class threadsafe_queue{
	public:
		threadsafe_queue() : basic_queue{}{};
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
