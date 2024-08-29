#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <sys/stat.h>
#include <dirent.h>
		 
#define BILLION  1000000000

#define NO_OP                       0
#define H_GATE                      1
#define S_GATE                      2
#define CNOT_GATE                   3
#define RX_GATE                     4
#define RY_GATE                     5
#define RZ_GATE                     6

#define START_BASE_PHYS             (0x0000000)
#define LOAD_BASE_PHYS              (0x0000008>>3)
#define DONE_BASE_PHYS              (0x0000010>>3)
#define QUBIT_BASE_PHYS             (0x0000018>>3)
#define QUBIT_NUM_BASE_PHYS         (0x0000020>>3)
                                              
#define QCTR_N_CUT_MEM_BASE_PHYS    (0x0040000>>3)
#define CORDIC1_MEM_BASE_PHYS       (0x0080000>>3)
#define CORDIC2_MEM_BASE_PHYS       (0x00C0000>>3)
#define GATE_MEM_BASE_PHYS          (0x0100000>>3)

// Read control
#define COMPLETE_BASE_PHYS          (0x0000000)
    
// Write/Read Data    
#define PING_MEM_BASE_PHYS          0x1000000
#define PONG_MEM_BASE_PHYS          0x2000000

#include "CGRA.h"
#include "FPGA_Driver.c"

int qubit;
int qubit_num;
U64 *Ping_Mem, *Pong_Mem;

int addr = 0;
void Initialize_Data(){
    Ping_Mem[0] = 0x3c000000;
    for(int k = 1; k < qubit; k++){
        Ping_Mem[k] = 0;
    }
    for(int k = 0; k < qubit; k++){
        Pong_Mem[k] = 0;
    }
    dma_write(0x10000, PING_MEM_BASE_PHYS, qubit);
    dma_write(0x20000, PONG_MEM_BASE_PHYS, qubit);
    
    // dma_read(0x10000, PING_MEM_BASE_PHYS, qubit);
    
    // for (int k = 0; k < qubit; k++) {
        // printf("%08x\n", Ping_Mem[k]);
    // }
}

// Function to convert float to 16-bit floating point (half-precision)
uint32_t float_to_hex(float f) {
    return *((uint32_t*)&f);
}

int32_t floatToFixedPoint32(float input) {
    // Define the scaling factor for the fractional part
    const int32_t scaleFactor = 1 << 30;  // 2^30
    
    // Check for overflow: if input exceeds the representable range, clip it
    if (input > 1.0f) {
        input = 1.0f;
    } else if (input < -1.0f) {
        input = -1.0f;
    }
    
    // Convert the float to fixed-point
    int32_t fixedPointValue = (int32_t)(input * scaleFactor);
    
    return fixedPointValue;
}

// Function to convert 32-bit fixed-point to float
float fixedPoint32ToFloat(int32_t fixedPointValue) {
    // Define the scaling factor for the fractional part
    const float scaleFactor = 1.0f / (1 << 30);  // 1 / 2^30
    
    // Convert the fixed-point value to float
    float floatValue = fixedPointValue * scaleFactor;
    
    return floatValue;
}

void Load(){
    *(CGRA_info.reg_mmap + LOAD_BASE_PHYS) = 1;
}

void Start(){
    *(CGRA_info.reg_mmap + START_BASE_PHYS) = 1;
}

void Done(){
    *(CGRA_info.reg_mmap + DONE_BASE_PHYS) = 1;
}

void Wait(){
    while(1){
        if((*(CGRA_info.reg_mmap + COMPLETE_BASE_PHYS)) == 1){
            break;
        }
    }
}

void Qubit(int n){
    qubit_num = n;
    qubit = (U64)pow(2, n) - 1;
    *(CGRA_info.reg_mmap + QUBIT_BASE_PHYS) = qubit;
    *(CGRA_info.reg_mmap + QUBIT_NUM_BASE_PHYS) = n;
}

void H_Gate(int n){
    U64 cut = (U64)pow(2, (qubit_num - n - 1));
    // printf("Applying H_Gate on qubit %d with cut %u\n", n, cut);
    *(CGRA_info.reg_mmap + QCTR_N_CUT_MEM_BASE_PHYS + addr) = ((U64)n << 17) | cut;
    *(CGRA_info.reg_mmap + CORDIC1_MEM_BASE_PHYS + addr) = 0;
    *(CGRA_info.reg_mmap + CORDIC2_MEM_BASE_PHYS + addr) = 0;
    *(CGRA_info.reg_mmap + GATE_MEM_BASE_PHYS + addr) = H_GATE;
    addr++;
}

void CNOT_Gate(int control, int target){
    U64 cut = (U64)pow(2, (qubit_num - target - 1));
    // printf("Applying H_Gate on qubit %d with cut %u\n", n, cut);
    *(CGRA_info.reg_mmap + QCTR_N_CUT_MEM_BASE_PHYS + addr) = ((U64) control << 22) |((U64)target << 17) | cut;
    *(CGRA_info.reg_mmap + CORDIC1_MEM_BASE_PHYS + addr) = 0;
    *(CGRA_info.reg_mmap + CORDIC2_MEM_BASE_PHYS + addr) = 0;
    *(CGRA_info.reg_mmap + GATE_MEM_BASE_PHYS + addr) = CNOT_GATE;
    addr++;
}

void S_Gate(int n){
    U64 cut = (U64)pow(2, (qubit_num - n - 1));
    // printf("Applying H_Gate on qubit %d with cut %u\n", n, cut);
    *(CGRA_info.reg_mmap + QCTR_N_CUT_MEM_BASE_PHYS + addr) = ((U64)n << 17) | 0;
    *(CGRA_info.reg_mmap + CORDIC1_MEM_BASE_PHYS + addr) = 0;
    *(CGRA_info.reg_mmap + CORDIC2_MEM_BASE_PHYS + addr) = 0;
    *(CGRA_info.reg_mmap + GATE_MEM_BASE_PHYS + addr) = S_GATE;
    addr++;
}

void RX_Gate(int n, float phi){
    U64 cut = (U64)pow(2, (qubit_num - n - 1));
    // printf("Applying H_Gate on qubit %d with cut %u\n", n, cut);
    *(CGRA_info.reg_mmap + QCTR_N_CUT_MEM_BASE_PHYS + addr) = ((U64)n << 17) | cut;
	    // Calculate sine and cosine
    float sin_phi = sin(phi/2);
    float cos_phi = cos(phi/2);

    // Convert to 16-bit floating point
    uint32_t sin_n_half = floatToFixedPoint32(sin_phi);
    uint32_t cos_n_half = floatToFixedPoint32(cos_phi);
	
    *(CGRA_info.reg_mmap + CORDIC1_MEM_BASE_PHYS + addr) = cos_n_half;
    *(CGRA_info.reg_mmap + CORDIC2_MEM_BASE_PHYS + addr) = sin_n_half;
    *(CGRA_info.reg_mmap + GATE_MEM_BASE_PHYS + addr) = RX_GATE;
    addr++;
}

void RZ_Gate(int n, float phi){
    U64 cut = (U64)pow(2, (qubit_num - n - 1));
    // printf("Applying H_Gate on qubit %d with cut %u\n", n, cut);
    *(CGRA_info.reg_mmap + QCTR_N_CUT_MEM_BASE_PHYS + addr) = ((U64)n << 17) | cut;
	    // Calculate sine and cosine
    float sin_phi = sin(phi/2);
    float cos_phi = cos(phi/2);

    // Convert to 16-bit floating point
    uint32_t sin_n_half = floatToFixedPoint32(sin_phi);
    uint32_t cos_n_half = floatToFixedPoint32(cos_phi);

    *(CGRA_info.reg_mmap + CORDIC1_MEM_BASE_PHYS + addr) = cos_n_half;
    *(CGRA_info.reg_mmap + CORDIC2_MEM_BASE_PHYS + addr) = sin_n_half;
    *(CGRA_info.reg_mmap + GATE_MEM_BASE_PHYS + addr) = RZ_GATE;
    addr++;
}

void RY_Gate(int n, float phi){
    U64 cut = (U64)pow(2, (qubit_num - n - 1));
    // printf("Applying H_Gate on qubit %d with cut %u\n", n, cut);
    *(CGRA_info.reg_mmap + QCTR_N_CUT_MEM_BASE_PHYS + addr) = ((U64)n << 17) | cut;
	    // Calculate sine and cosine
    float sin_phi = sin(phi/2);
    float cos_phi = cos(phi/2);

    // Convert to 16-bit floating point
    uint32_t sin_n_half = floatToFixedPoint32(sin_phi);
    uint32_t cos_n_half = floatToFixedPoint32(cos_phi);
	
    *(CGRA_info.reg_mmap + CORDIC1_MEM_BASE_PHYS + addr) = cos_n_half;
    *(CGRA_info.reg_mmap + CORDIC2_MEM_BASE_PHYS + addr) = sin_n_half;
    *(CGRA_info.reg_mmap + GATE_MEM_BASE_PHYS + addr) = RY_GATE;
    addr++;
}

// Function to convert half-precision floating point to single-precision floating point
float half_to_float(uint32_t h) {
    uint32_t h_exp = (h >> 10) & 0x1F;  // Extract exponent
    uint32_t h_mant = h & 0x3FF;        // Extract mantissa
    uint32_t h_sign = h >> 15;          // Extract sign

    uint32_t f_sign = h_sign << 31;     // Sign bit for float
    uint32_t f_exp;
    uint32_t f_mant;

    if (h_exp == 0) {
        // Zero / Subnormal
        if (h_mant == 0) {
            // Zero
            f_exp = 0;
            f_mant = 0;
        } else {
            // Subnormal
            int shift = __builtin_clz(h_mant) - 21; // Adjust shift for 32-bit float
            f_exp = (127 - 15 - shift) << 23;
            f_mant = (h_mant << (shift + 1)) & 0x7FFFFF;
        }
    } else if (h_exp == 0x1F) {
        // Infinity / NaN
        f_exp = 0xFF << 23;
        f_mant = h_mant << 13;
    } else {
        // Normalized
        f_exp = (h_exp + (127 - 15)) << 23;
        f_mant = h_mant << 13;
    }

    uint32_t f = f_sign | f_exp | f_mant;
    float result;
    memcpy(&result, &f, sizeof(result));
    return result;
}

void print_single_precision(uint64_t value) {
    // Extract the most significant 32 bits (real part)
    uint32_t msb = value >> 32; 
    
    // Extract the least significant 32 bits (imaginary part)
    uint32_t lsb = value & 0xFFFFFFFF; 
    
    // Interpret the extracted bits as floats
    float real = *((float*)&msb);
    float imag = *((float*)&lsb);
    
    // Print the real and imaginary parts
    printf("%f + %fj\n", real, imag);
}

void qft_rotations_Qsun(int num_qubits) {
    if (num_qubits == 0) {
        return;
    }

    num_qubits -= 1;
    H_Gate(num_qubits);

    for (int j = 0; j < num_qubits; j++) {
        RZ_Gate(num_qubits, 3.14159265359 / pow(2, (num_qubits - j)) / 2);
        CNOT_Gate(j, num_qubits);
        RZ_Gate(num_qubits, -3.14159265359 / pow(2, (num_qubits - j)) / 2);
        CNOT_Gate(j, num_qubits);
        RZ_Gate(num_qubits, 3.14159265359 / pow(2, (num_qubits - j)) / 2);
    }

    qft_rotations_Qsun(num_qubits);  // Đệ quy để tiếp tục cho tới khi num_qubits == 0
}

void swap_registers_Qsun(int num_qubits) {
    for (int j = 0; j < num_qubits / 2; j++) {
        CNOT_Gate(j, num_qubits - j - 1);
        CNOT_Gate(num_qubits - j - 1, j);
        CNOT_Gate(j, num_qubits - j - 1);
    }
}

void write_single_precision_to_file(FILE *file, uint64_t value) {
    // Extract the most significant 32 bits (real part)
    uint32_t msb = value >> 32;
    
    // Extract the least significant 32 bits (imaginary part)
    uint32_t lsb = value & 0xFFFFFFFF;
    
    // Interpret the extracted bits as floats
    float real = fixedPoint32ToFloat(msb);
    float imag = fixedPoint32ToFloat(lsb);
    
    // Write the real and imaginary parts to the file
    fprintf(file, "%f\n%f\n", real, imag);
}

void QRC(char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        printf("Error: Could not open file here%s\n", filename);
        return;
    }
	
    char line[100];
    char gateType[10];
    int params[2];
    double angle;

    while (fgets(line, sizeof(line), file)) {
        trim(line);  // Trim leading and trailing spaces

        // Skip lines with just [ or ]
        if (line[0] == '[' || line[0] == ']') {
            continue;
        }

        // Parse for S and H gates
        if (sscanf(line, "('%[^']', [%d], -999)", gateType, &params[0]) == 2) {
            if (strcmp(gateType, "S") == 0) {
                S_Gate(params[0]);
            } else if (strcmp(gateType, "H") == 0) {
                H_Gate(params[0]);
            }
        }
        // Parse for CNOT gate
        if (sscanf(line, "('%[^']', [%d , %d], %lf)", gateType, &params[0], &params[1], &angle) == 4) {
            if (strcmp(gateType, "CNOT") == 0) {
                CNOT_Gate(params[0], params[1]);
            }
        }
        // Parse for RX, RY, RZ gates
        else if (sscanf(line, "('%[^']', [%d], %lf)", gateType, &params[0], &angle) == 3) {
            if (strcmp(gateType, "RX") == 0) {
                RX_Gate(params[0], angle);
            } else if (strcmp(gateType, "RY") == 0) {
                RY_Gate(params[0], angle);
            } else if (strcmp(gateType, "RZ") == 0) {
                RZ_Gate(params[0], angle);
            }
        }
    }

    fclose(file);
}

// Function to generate a random float between 0 and 2*π
float random_0_to_2pi() {
	// Generate a random number between 0 and 1
    double randomValue = (double)rand() / RAND_MAX;

    // Scale the random number to the range [0, 2*pi]
    double result = randomValue * 2 * M_PI;

    return result;
}

// Function to shuffle an array
void shuffle_array(int* array, int n) {
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

// Function to choose a value from 1 to max_value (inclusive)
int choose_from_array(int max_value) {
    // Generate a random number between 0 and 3
    int random_chance = rand() % 4;

    // 25% chance to return 2
    if (random_chance == 1) {
        return 2;
    }

    // 75% chance to return a random number between 1 and max_value
    return 1;
}

void qrc_Qsun(int num_qubits, int depth) {
	 srand(time(NULL) ^ getpid());
    int max_operands = 2;
	
    for (int i = 0; i < depth; i++) {
		
        int remaining_qubits[num_qubits];
        for (int j = 0; j < num_qubits; j++) {
            remaining_qubits[j] = j;
        }
        int remaining_count = num_qubits;
		int num_op_pool;
        while (remaining_count > 0) {
			 
            int max_possible_operands = remaining_count < max_operands ? remaining_count : max_operands;
            int num_operands = choose_from_array(max_possible_operands);
			// printf("num_operands = %d \n",num_operands);
            shuffle_array(remaining_qubits, remaining_count);
			for (int j = 0; j < remaining_count; j++) {
				// printf("remaining_qubits[%d] = %d \n",j,remaining_qubits[j]);
			}
			
            int operands[num_operands];
            for (int j = 0; j < num_operands; j++) {
                operands[j] = remaining_qubits[j];
            }
			
            remaining_count -= num_operands;
			// printf("remaining_count = %d \n",remaining_count);
            for (int j = 0; j < remaining_count; j++) {
                remaining_qubits[j] = remaining_qubits[j + num_operands];
            }
            // Randomly select and apply a quantum gate
            if (num_operands == 1) { 
                num_op_pool = rand()%5;
				// printf("----------num_op_pool = %d\n",num_op_pool);
                switch(num_op_pool) {
                    case 0:
						// printf("Applying H_Gate\n");
                        H_Gate(operands[0]);
                        break;
                    case 1:
						// printf("Applying S_Gate\n");
                        S_Gate(operands[0]);
                        break;
                    case 2:
						// printf("Applying RX_Gate\n");
                        RX_Gate(operands[0], random_0_to_2pi());
                        break;
                    case 3:
						// printf("Applying RY_Gate\n");
                        RY_Gate(operands[0], random_0_to_2pi());
                        break;
                    case 4:
						// printf("Applying RZ_Gate\n");
                        RZ_Gate(operands[0], random_0_to_2pi());
                        break;
                }
            } else {
				// printf("Applying CNOT_Gate\n");
                CNOT_Gate(operands[0], operands[1]);
            }
        }
    }
}

int main(){
    unsigned char* membase;
    if (cgra_open() == 0)
        exit(1);
    
    cgra.dma_ctrl = CGRA_info.dma_mmap;
    membase = (unsigned char*) CGRA_info.ddr_mmap;
    
    printf("membase: %llx\n", (U64)membase);
    
    Ping_Mem = (U64*)(membase + PING_MEM_BASE_PHYS);
    Pong_Mem = (U64*)(membase + PONG_MEM_BASE_PHYS);
    
	// delete the output directory
		char output_dir[] = "output";
		DIR* dir = opendir(output_dir);
		if (dir) {
			closedir(dir);
			// directory exists, remove it recursively
			if (system("rm -rf output") != 0) {
				fprintf(stderr, "error deleting output directory\n");
				exit(1);
			}
		}
			
    // Specify the input and output files
	
	int run_from = 1;
	int step = 99;
	
	struct timespec start_execution, end_execution;
	unsigned long long time_spent_execution[100];
	unsigned long long sum_time_spent_execution;
	
		for(int depth = 1; depth < 11; depth++){
			// Create directory structure
                char dir_path[100];
                snprintf(dir_path, sizeof(dir_path), "time/");
                
				// // Create the directory using system()
                char command[150]; // Adjust the size as needed
                snprintf(command, sizeof(command), "mkdir -p %s", dir_path);
                if (system(command)) {
                    fprintf(stderr, "Error creating directory: %s\n", dir_path);
                    exit(1);
                }
				
				// //define the output file name
				char filename[100];
				sprintf(filename, "time/FX32_%d_Time.txt", depth );

				FILE *file = fopen(filename, "w");

				if (file == NULL) {
					printf("Cannot open the file %s !\n", filename);
					return 1;
				}
				
				char filename2[100];
				sprintf(filename2, "time/FP32_%d_TimeSTD.txt", depth );

				FILE *file2 = fopen(filename2, "w");

				if (file2 == NULL) {
					printf("Cannot open the file %s !\n", filename2);
					return 1;
				}
			for(int num_qubits = 3; num_qubits < 18; num_qubits++){
				sum_time_spent_execution = 0;
				for(int loop = run_from; loop <= run_from+step; loop++){
					time_spent_execution[loop] = 0;
					addr = 0;

					clock_gettime(CLOCK_REALTIME, &start_execution);
					Qubit(num_qubits);  // Set the number of qubits before initializing and printing memory
					Ping_Mem[0] = 0x4000000000000000;
					for(int k = 1; k < qubit+1; k++){
						Ping_Mem[k] = 0;
					}
					
					for(int k = 0; k < qubit+1; k++){
						Pong_Mem[k] = 0;
					}
					
					Load(); 

					qrc_Qsun(num_qubits,depth);
					
					dma_write(PING_MEM_BASE_PHYS, PING_MEM_BASE_PHYS, qubit+1);
					dma_write(PONG_MEM_BASE_PHYS, PONG_MEM_BASE_PHYS, qubit+1);
					
					Start();
					Wait();
					if((addr&0x1) == 1){
						dma_read(PONG_MEM_BASE_PHYS, PONG_MEM_BASE_PHYS, qubit+1);
					}
					else {
						dma_read(PING_MEM_BASE_PHYS, PING_MEM_BASE_PHYS, qubit+1);
					}
					Done();
					clock_gettime(CLOCK_REALTIME, &end_execution);
					time_spent_execution[loop] = BILLION * (end_execution.tv_sec - start_execution.tv_sec) + (end_execution.tv_nsec - start_execution.tv_nsec);
					
					clock_gettime(CLOCK_REALTIME, &end_execution);
					sum_time_spent_execution = BILLION * (end_execution.tv_sec - start_execution.tv_sec) + (end_execution.tv_nsec - start_execution.tv_nsec) + sum_time_spent_execution;
					
			}
			
			fprintf(file,"%f\n", (double)sum_time_spent_execution/ (BILLION*100.0)); //
			
			// Calculate mean execution time
            double mean_time = (double)sum_time_spent_execution / (step + 1);
			
			double sum_squared_diff = 0.0;
            for (int i = 0; i <= step; i++) {
                sum_squared_diff += pow(time_spent_execution[i] - mean_time, 2);
            }
            double std_deviation = sqrt(sum_squared_diff / (step + 1));

			fprintf(file2,"%f\n", (double)std_deviation/ (BILLION*100.0)); //
			
			printf("Time = %f\n", (double)sum_time_spent_execution/ (BILLION*100.0)); //
			printf("STD = %f\n", (double)std_deviation/ (BILLION*100.0)); //
		}
		fclose(file);
		fclose(file2);
	}
	
    return 0;
}
