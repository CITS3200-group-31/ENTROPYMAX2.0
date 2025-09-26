#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <csv_file_path1> <csv_file_path2>\n", argv[0]);
        return 1;
    }

    char command[1024]; 
    snprintf(command, sizeof(command), "python3 run_converter.py \"%s\" \"%s\"", argv[1], argv[2]);

    int ret = system(command);
    if (ret != 0) {
        fprintf(stderr, "Python script failed with exit code %d\n", ret);
        return ret;
    }

    printf("Conversion successful.\n");
    return 0;
}