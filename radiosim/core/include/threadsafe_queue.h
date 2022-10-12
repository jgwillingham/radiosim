
#ifndef THREADSAFEQUEUE_INCLUDED
#define THREADSAFEQUEUE_INCLUDED

#include <mutex>
#include <condition_variable>
#include <queue>

template<typename T>
class threadsafe_queue{
	public:
		threadsafe_queue() : basic_queue{}{};
		void push(const T& val){
			std::unique_lock<std::mutex> lock(mutex);
			bool was_empty = basic_queue.empty();
			basic_queue.push(val);
			lock.unlock();
			if (was_empty){
				queue_condition.notify_one();
			}
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
		void wait_pop(T& output){
			std::unique_lock<std::mutex> lock(mutex);
			while (basic_queue.empty()){
				queue_condition.wait(lock);
			}
			output = basic_queue.front();
			basic_queue.pop();
		}
	private:
		std::queue<T> basic_queue;
		std::mutex mutex;
		std::condition_variable queue_condition;
};


#endif
