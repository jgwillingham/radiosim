
#ifndef RINGBUFFER_INCLUDED
#define RINGBUFFER_INCLUDED

#include <vector>
#include <mutex>
#include <memory>

template<typename T>
class ring_buffer{
	public:
		ring_buffer(size_t size) : maxsize{size}, container(std::unique_ptr<T[]>(new T[size])) {};

		// put a single item into the buffer
		void put(T item){
			std::lock_guard<std::mutex> lock(mutex);
			container[write_idx] = item;
			write_idx = (write_idx + 1) % maxsize;

			if (isfull){ // buffer overflow. overwriting data
				read_idx = (read_idx + 1) % maxsize;
			}

			isfull = read_idx==write_idx;
		};

		// put a vector of items into the buffer
		void put(std::vector<T> new_items){
			std::lock_guard<std::mutex> lock(mutex);
			for (auto& item : new_items){
				container[write_idx] = item;
				write_idx = (write_idx + 1) % maxsize;

				if (isfull){ // buffer overflow. overwriting data
					read_idx = (read_idx + 1) % maxsize;
				}

				isfull = read_idx==write_idx;
			}
		};

		// get single item
		T get(){
			std::lock_guard<std::mutex> lock(mutex);
			if (empty(false)){
				return T();
			}
			T value = container[read_idx];
			isfull = false;
			read_idx = (read_idx + 1) % maxsize;
			return value;
		};

		// get multiple items (returns a vector)
		std::vector<T> get(size_t nitems){
			std::lock_guard<std::mutex> lock(mutex);

			std::vector<T> output_items(nitems);
			for (size_t i=0; i<nitems; i++){
				if (empty(false)){
					output_items[i] = T();
					continue;
				}
				output_items[i] = container[read_idx];
				isfull = false;
				read_idx = (read_idx + 1) % maxsize;
			}
			return output_items;
		};

		// is the buffer empty?
		bool empty(bool safe=true){
			if (safe){
				std::lock_guard<std::mutex> lock(mutex);
			};
			return (read_idx == write_idx) and not isfull;
		};


	private:
		size_t maxsize;
		std::unique_ptr<T[]> container;

		size_t read_idx = 0;
		size_t write_idx = 0;
		bool isfull = false;

		std::mutex mutex;

};


#endif
