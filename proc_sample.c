/*
 * Operating System Process Management Implementation Sample
 * A simplified version demonstrating key OS concepts and system programming skills
 */

#include <stdlib.h>
#include <string.h>

typedef struct process {
    int pid;
    char name[256];
    struct process *parent;
    list_t threads;
    list_t children;
    void *page_directory;
    int status;
    int state;
    /* Additional process metadata */
} process_t;

/* Process states */
#define PROC_RUNNING    1
#define PROC_DEAD       2

/* Initialize process management subsystem */
void 
process_system_init() 
{
    /* Initialize process list and allocator */
}

/* Create a new process */
process_t*
process_create(char *name)
{
    process_t *proc = malloc(sizeof(process_t));
    
    /* Generate unique process ID */
    proc->pid = generate_next_pid();
    
    /* Initialize process metadata */
    strncpy(proc->name, name, sizeof(proc->name)-1);
    init_list(&proc->threads);
    init_list(&proc->children);
    
    /* Set up memory management */
    proc->page_directory = create_page_directory();
    
    /* Handle parent/child relationship */
    if (current_process) {
        proc->parent = current_process;
        add_child_process(current_process, proc);
    }
    
    return proc;
}

/* Clean up process resources */
void
process_cleanup(process_t *proc, int exit_status) 
{
    /* Save exit status */
    proc->status = exit_status;
    proc->state = PROC_DEAD;
    
    /* Clean up memory mappings */
    cleanup_process_memory(proc);
    
    /* Handle child processes */
    reparent_children(proc);
    
    /* Release other resources */
    cleanup_process_resources(proc);
    
    /* Wake up waiting parent */
    if (proc->parent && proc->parent->waiting)
        wake_up_process(proc->parent);
}

/* Wait for child process to exit */
int
process_wait(int pid, int *status)
{
    process_t *child;
    
    /* Handle wait for any child case */
    if (pid == -1) {
        while ((child = find_zombie_child(current_process))) {
            int child_pid = child->pid;
            *status = child->status;
            cleanup_zombie_process(child);
            return child_pid;
        }
    }
    
    /* Handle wait for specific child */
    if ((child = find_child_process(current_process, pid))) {
        while (child->state != PROC_DEAD) {
            sleep_current_process();
        }
        *status = child->status;
        cleanup_zombie_process(child);
        return pid;
    }
    
    return -1; /* No such child */
}