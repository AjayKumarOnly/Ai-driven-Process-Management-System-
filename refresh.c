#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#define MAX 100

int A[MAX], B[MAX], C[MAX];
int n;

void *add_vector(void *arg)
{
    int thread_id = *(int *)arg;

    int start = thread_id * (n / 3);
    int end;

    if (thread_id == 2)
        end = n;
    else
        end = start + (n / 3);

    for (int i = start; i < end; i++)
        C[i] = A[i] + B[i];

    pthread_exit(NULL);
}

int main()
{
    pthread_t threads[3];
    int id[3];

    printf("Enter size of vectors: ");
    scanf("%d", &n);

    printf("Enter elements of Vector A:\n");
    for (int i = 0; i < n; i++)
        scanf("%d", &A[i]);

    printf("Enter elements of Vector B:\n");
    for (int i = 0; i < n; i++)
        scanf("%d", &B[i]);

    for (int i = 0; i < 3; i++)
    {
        id[i] = i;
        pthread_create(&threads[i], NULL, add_vector, &id[i]);
    }

    for (int i = 0; i < 3; i++)
        pthread_join(threads[i], NULL);

    printf("\nResultant Vector:\n");

    for (int i = 0; i < n; i++)
        printf("%d ", C[i]);

    printf("\n");

    return 0;
}

#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

int shared_variable;

pthread_mutex_t lock;

void *reader(void *arg)
{
    int id = *(int *)arg;

    pthread_mutex_lock(&lock);

    int value = shared_variable;
    printf("Reader %d: Shared value = %d, Square = %d\n",
           id, value, value * value);

    pthread_mutex_unlock(&lock);

    pthread_exit(NULL);
}

void *writer(void *arg)
{
    int id = *(int *)arg;

    pthread_mutex_lock(&lock);

    printf("Writer %d: Old value = %d\n", id, shared_variable);

    shared_variable += 5;

    printf("Writer %d: New value = %d\n", id, shared_variable);

    pthread_mutex_unlock(&lock);

    pthread_exit(NULL);
}

int main()
{
    pthread_t readers[3], writers[2];

    int reader_id[3] = {1, 2, 3};
    int writer_id[2] = {1, 2};

    printf("Enter initial value of shared variable: ");
    scanf("%d", &shared_variable);

    pthread_mutex_init(&lock, NULL);

    for (int i = 0; i < 2; i++)
        pthread_create(&writers[i], NULL, writer, &writer_id[i]);

    for (int i = 0; i < 3; i++)
        pthread_create(&readers[i], NULL, reader, &reader_id[i]);

    for (int i = 0; i < 2; i++)
        pthread_join(writers[i], NULL);

    for (int i = 0; i < 3; i++)
        pthread_join(readers[i], NULL);

    printf("\nFinal shared variable = %d\n", shared_variable);

    pthread_mutex_destroy(&lock);

    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mman.h>
#include <semaphore.h>

typedef struct {
    int value[3];
    sem_t mutex;
} Shared;

int main()
{
    Shared *shm;

    // Create shared memory
    shm = mmap(NULL, sizeof(Shared),
               PROT_READ | PROT_WRITE,
               MAP_SHARED | MAP_ANONYMOUS, -1, 0);

    // Initialize semaphore
    sem_init(&shm->mutex, 1, 1);

    for (int i = 0; i < 3; i++)
    {
        if (fork() == 0)
        {
            int value;

            printf("Enter value for Process %d: \n", i + 1);
            scanf("%d", &value);

            // Lock semaphore
            sem_wait(&shm->mutex);

            shm->value[i] = value;

            // Unlock semaphore
            sem_post(&shm->mutex);

            exit(0);
        }
    }

    // Parent waits for all 3 processes
    for (int i = 0; i < 3; i++)
        wait(NULL);

    // Calculate sum
    int sum = shm->value[0] + shm->value[1] + shm->value[2];

    printf("\nValues: %d %d %d\n",
           shm->value[0],
           shm->value[1],
           shm->value[2]);

    printf("Sum = %d\n", sum);


    return 0;
}

#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

int A, B;

pthread_mutex_t lockA;
pthread_mutex_t lockB;

void *transaction1(void *arg)
{
    printf("T1: Trying to lock A\n");
    pthread_mutex_lock(&lockA);

    printf("T1: Locked A\n");

    sleep(1);

    printf("T1: Trying to lock B\n");
    pthread_mutex_lock(&lockB);

    printf("T1: Locked B\n");

    A++;
    B++;

    pthread_mutex_unlock(&lockB);
    pthread_mutex_unlock(&lockA);

    return NULL;
}

void *transaction2(void *arg)
{
    printf("T2: Trying to lock B\n");
    pthread_mutex_lock(&lockB);

    printf("T2: Locked B\n");

    sleep(1);

    printf("T2: Trying to lock A\n");
    pthread_mutex_lock(&lockA);

    printf("T2: Locked A\n");

    B++;
    A++;

    pthread_mutex_unlock(&lockA);
    pthread_mutex_unlock(&lockB);

    return NULL;
}

int main()
{
    pthread_t t1, t2;

    printf("Enter initial value of A: ");
    scanf("%d", &A);

    printf("Enter initial value of B: ");
    scanf("%d", &B);

    pthread_mutex_init(&lockA, NULL);
    pthread_mutex_init(&lockB, NULL);

    pthread_create(&t1, NULL, transaction1, NULL);
    pthread_create(&t2, NULL, transaction2, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("Final A = %d\n", A);
    printf("Final B = %d\n", B);

    return 0;
}

#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

int A, B;

pthread_mutex_t lockA;
pthread_mutex_t lockB;

void *transaction1(void *arg)
{
    printf("T1: Locking A\n");
    pthread_mutex_lock(&lockA);

    printf("T1: Locking B\n");
    pthread_mutex_lock(&lockB);

    A++;
    B++;

    printf("T1: Updated A and B\n");

    pthread_mutex_unlock(&lockB);
    pthread_mutex_unlock(&lockA);

    return NULL;
}

void *transaction2(void *arg)
{
    printf("T2: Locking A\n");
    pthread_mutex_lock(&lockA);

    printf("T2: Locking B\n");
    pthread_mutex_lock(&lockB);

    A++;
    B++;

    printf("T2: Updated A and B\n");

    pthread_mutex_unlock(&lockB);
    pthread_mutex_unlock(&lockA);

    return NULL;
}

int main()
{
    pthread_t t1, t2;

    printf("Enter initial value of A: ");
    scanf("%d", &A);

    printf("Enter initial value of B: ");
    scanf("%d", &B);

    pthread_mutex_init(&lockA, NULL);
    pthread_mutex_init(&lockB, NULL);

    pthread_create(&t1, NULL, transaction1, NULL);
    pthread_create(&t2, NULL, transaction2, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("\nDeadlock prevented.\n");

    printf("Final value of A = %d\n", A);
    printf("Final value of B = %d\n", B);

    return 0;
}

#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

int A, B;

pthread_mutex_t lockA;
pthread_mutex_t lockB;

void *transaction1(void *arg)
{
    while (1)
    {
        pthread_mutex_lock(&lockA);

        printf("T1: Locked A\n");

        if (pthread_mutex_trylock(&lockB) == 0)
        {
            printf("T1: Locked B\n");

            A++;
            B++;

            pthread_mutex_unlock(&lockB);
            pthread_mutex_unlock(&lockA);

            printf("T1: Transaction completed\n");
            break;
        }
        else
        {
            printf("T1: B is unavailable. Rolling back...\n");

            pthread_mutex_unlock(&lockA);

            sleep(1);
        }
    }

    return NULL;
}

void *transaction2(void *arg)
{
    while (1)
    {
        pthread_mutex_lock(&lockB);

        printf("T2: Locked B\n");

        if (pthread_mutex_trylock(&lockA) == 0)
        {
            printf("T2: Locked A\n");

            B++;
            A++;

            pthread_mutex_unlock(&lockA);
            pthread_mutex_unlock(&lockB);

            printf("T2: Transaction completed\n");
            break;
        }
        else
        {
            printf("T2: A is unavailable. Rolling back...\n");

            pthread_mutex_unlock(&lockB);

            sleep(1);
        }
    }

    return NULL;
}

int main()
{
    pthread_t t1, t2;

    printf("Enter initial value of A: ");
    scanf("%d", &A);

    printf("Enter initial value of B: ");
    scanf("%d", &B);

    pthread_mutex_init(&lockA, NULL);
    pthread_mutex_init(&lockB, NULL);

    pthread_create(&t1, NULL, transaction1, NULL);
    pthread_create(&t2, NULL, transaction2, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    printf("\nDeadlock recovery completed.\n");

    printf("Final value of A = %d\n", A);
    printf("Final value of B = %d\n", B);

    return 0;
}

#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define N 5

sem_t forks[N];

void *philosopher(void *arg)
{
    int i = *(int *)arg;

    printf("Philosopher %d is THINKING\n", i + 1);
    sleep(1);

    printf("Philosopher %d is HUNGRY\n", i + 1);

    // Pick up left fork
    sem_wait(&forks[i]);

    // Pick up right fork
    sem_wait(&forks[(i + 1) % N]);

    printf("Philosopher %d is EATING\n", i + 1);
    sleep(1);

    // Put down left fork
    sem_post(&forks[i]);

    // Put down right fork
    sem_post(&forks[(i + 1) % N]);

    printf("Philosopher %d is THINKING again\n", i + 1);

    return NULL;
}

int main()
{
    pthread_t philosophers[N];
    int id[N];

    // Initialize semaphores
    for (int i = 0; i < N; i++)
        sem_init(&forks[i], 0, 1);

    // Create philosophers
    for (int i = 0; i < N; i++)
    {
        id[i] = i;
        pthread_create(&philosophers[i], NULL, philosopher, &id[i]);
    }

    // Wait for philosophers
    for (int i = 0; i < N; i++)
        pthread_join(philosophers[i], NULL);


    return 0;
}
#include <stdio.h>

int main()
{
    int n, tq;

    printf("Enter number of processes: ");
    scanf("%d", &n);

    int bt[n], rt[n], ct[n], tat[n], wt[n];

    printf("Enter burst time:\n");

    for (int i = 0; i < n; i++)
    {
        printf("P%d: ", i + 1);
        scanf("%d", &bt[i]);
        rt[i] = bt[i];
    }

    printf("Enter time quantum: ");
    scanf("%d", &tq);

    int time = 0;
    int completed = 0;

    printf("\nGantt Chart:\n");

    while (completed < n)
    {
        for (int i = 0; i < n; i++)
        {
            if (rt[i] > 0)
            {
                printf("| P%d ", i + 1);

                if (rt[i] > tq)
                {
                    time = time + tq;
                    rt[i] = rt[i] - tq;
                }
                else
                {
                    time = time + rt[i];
                    rt[i] = 0;

                    ct[i] = time;
                    completed++;
                }
            }
        }
    }

    printf("|\n");

    float avg_tat = 0, avg_wt = 0;

    printf("\nProcess\tBT\tCT\tTAT\tWT\n");

    for (int i = 0; i < n; i++)
    {
        tat[i] = ct[i];       // AT = 0
        wt[i] = tat[i] - bt[i];

        avg_tat = avg_tat + tat[i];
        avg_wt = avg_wt + wt[i];

        printf("P%d\t%d\t%d\t%d\t%d\n",
               i + 1, bt[i], ct[i], tat[i], wt[i]);
    }

    printf("\nAverage TAT = %.2f", avg_tat / n);
    printf("\nAverage WT = %.2f\n", avg_wt / n);

    return 0;
}
#include <stdio.h>

int main()
{
    int n;

    printf("Enter number of processes: ");
    scanf("%d", &n);

    int at[n], bt[n], rt[n], ct[n], tat[n], wt[n];

    for (int i = 0; i < n; i++)
    {
        printf("Enter AT and BT for P%d: ", i + 1);
        scanf("%d %d", &at[i], &bt[i]);

        rt[i] = bt[i];
    }

    int time = 0;
    int completed = 0;

    printf("\nGantt Chart:\n");

    while (completed < n)
    {
        int shortest = -1;

        for (int i = 0; i < n; i++)
        {
            if (at[i] <= time && rt[i] > 0)
            {
                if (shortest == -1 || rt[i] < rt[shortest])
                {
                    shortest = i;
                }
            }
        }

        if (shortest == -1)
        {
            time++;
            continue;
        }

        printf("| P%d ", shortest + 1);

        rt[shortest]--;
        time++;

        if (rt[shortest] == 0)
        {
            ct[shortest] = time;
            completed++;
        }
    }

    printf("|\n");

    float avg_tat = 0, avg_wt = 0;

    printf("\nProcess\tAT\tBT\tCT\tTAT\tWT\n");

    for (int i = 0; i < n; i++)
    {
        tat[i] = ct[i] - at[i];
        wt[i] = tat[i] - bt[i];

        avg_tat += tat[i];
        avg_wt += wt[i];

        printf("P%d\t%d\t%d\t%d\t%d\t%d\n",
               i + 1, at[i], bt[i], ct[i], tat[i], wt[i]);
    }

    printf("\nAverage TAT = %.2f", avg_tat / n);
    printf("\nAverage WT = %.2f\n", avg_wt / n);

    return 0;
}
