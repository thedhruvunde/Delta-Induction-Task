# include <stdio.h>
# define SECRET_VALUE 315525
# define LEN 30

int main(){
    char str[LEN];
    char flag[] = "Good Job! Here is the flag";
    int val = 0;
    printf("Enter the string : ");
    fgets(str, LEN, stdin);

    for(int i = 0; i < LEN; i++){
        if(str[i] == '\n'){
            break;
        }
        else{
            val += ((str[i] * str[i]) + (str[i] * (100 - i)) + i + (str[i] * 7) + ((str[i]|i)&(i+3)));
            val -=  ((str[i] * str[i]) % (i + 1 ));
        }
    }

    printf("Calculated value : %d\n", val);
    if (val == SECRET_VALUE){
        printf("%s\n", flag);
    }
    else{
        printf("Wrong string\n");
    }
}
