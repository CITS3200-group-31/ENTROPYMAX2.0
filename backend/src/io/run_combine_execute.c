#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: %s <main_csv_file> <gps_parquet_file> <output_parquet_file>\n", argv[0]);
        return 1;
    }

    char command[1024];
    snprintf(command, sizeof(command), "python3 run_combine.py \"%s\" \"%s\" \"%s\"",
            argv[1], argv[2], argv[3]);

    int ret = system(command);

    if (ret != 0) {
        printf("Error: Python script failed with exit code %d\n", ret);
        return ret;
    }

    printf("Merge completed successfully.\n");
    return 0;
}
