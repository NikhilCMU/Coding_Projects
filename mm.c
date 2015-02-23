/*
* mm.c
*

Nikhil Nilakantan 
nnilakan

Using first-fit technique with placing newly freed blocks at front
of free list after coalscing.

HEADER | PREVIOUS BLOCK POINTER | NEXT BLOCK POINTER | DATA | FOOTER
4 | 8 | 8 | ? | 4

Allocated blocks simply have HEADER | PAYLOAD | PADDING (OPTIONAL) | FOOTER

bp is always address of previous block pointer!

* NOTE TO STUDENTS: Replace this header comment with your own header
* comment that gives a high level description of your solution.
*/
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>

#include "mm.h"
#include "memlib.h"

/* If you want debugging output, use the following macro.  When you hand
* in, remove the #define DEBUG line. */
//#define DEBUG
#ifdef DEBUG
# define dbg_printf(...) printf(__VA_ARGS__)
#else
# define dbg_printf(...)
#endif


/* do not change the following! */
#ifdef DRIVER
/* create aliases for driver tests */
#define malloc mm_malloc
#define free mm_free
#define realloc mm_realloc
#define calloc mm_calloc
#endif /* def DRIVER */

/* single word (4) or double word (8) alignment */
#define ALIGNMENT 8

/* minimum block size */
#define MIN_BLOCK_SIZE 24

/* rounds up to the nearest multiple of ALIGNMENT */
#define ALIGN(p) (((size_t)(p) + (ALIGNMENT-1)) & ~0x7)

/* Basic constants and macros */
#define WSIZE 4 /* Word and header/footer size (bytes) */
#define DSIZE 8 /* Double word size (bytes) */
#define PTR_SIZE 8 /* Size of pointer in 64-bit system */

#define CHUNKSIZE (1<<8) /* Extend heap by this amount (bytes) */

#define MAX(x, y) ((x) > (y) ? (x) : (y))

/* Pack a size and allocated bit into a word */
#define PACK(size, alloc) ((size) | (alloc))

/* Read and write a word at address p */
#define GET(p) (*(unsigned int *)(p))
#define PUT(p, val) (*(unsigned int *)(p) = (val))

/* Read the size and allocated fields from address p */
#define GET_SIZE(p) (GET(p) & ~0x7)
#define GET_ALLOC(p) (GET(p) & 0x1)

#define SIZE_T_SIZE (ALIGN(sizeof(size_t)))

#define SIZE_PTR(p)  ((size_t*)(((char*)(p)) - SIZE_T_SIZE))

/* Given block ptr bp, compute address of its header and footer */
#define HDRP(bp) ((char *)(bp) - WSIZE)
#define FTRP(bp) ((char *)(bp) + GET_SIZE(HDRP(bp)) - DSIZE)

/* Given block ptr bp, compute address of next and previous blocks */
#define NEXT_BLKP(bp) ((char *)(bp) + GET_SIZE(HDRP(bp)))
#define PREV_BLKP(bp) ((char *)(bp) - GET_SIZE(HDRP(bp) - WSIZE))

/* Given block ptr bp, compute address of next and previous free blocks */
#define NEXT_FREE_BLKP(bp) (*(void **)(bp + DSIZE))
#define PREV_FREE_BLKP(bp) (*(void **)(bp))

static char *heap_listp = 0;
static char *free_listp = 0;

static void *find_fit(size_t size);
static void *extend_heap(size_t words);
static void place(void *bp, size_t asize);
static void deleteBlk(void *bp);
static void *coalesce(void *bp);
static void reinsert(void *bp);


/*
* Initialize: return -1 on error, 0 on success.
*/
int mm_init(void) {

    if ((heap_listp = mem_sbrk(2 * MIN_BLOCK_SIZE)) == NULL) {
        return -1;
    }

    PUT(heap_listp, 0);
    PUT(heap_listp + (WSIZE), PACK(MIN_BLOCK_SIZE, 1));

    PUT(heap_listp + (2*WSIZE), 0);
    PUT(heap_listp + (3*WSIZE), 0);

    PUT(heap_listp + (MIN_BLOCK_SIZE), PACK(MIN_BLOCK_SIZE, 1));

    /* End of heap marker */
    PUT(heap_listp + WSIZE + MIN_BLOCK_SIZE, PACK(0, 1)); 

    free_listp = heap_listp + DSIZE;

    if (extend_heap(CHUNKSIZE/WSIZE) == NULL)
        return -1;
    return 0;
}

/* Extends the heap by asking for more space, and reassigning pointers
accordingly. */
static void *extend_heap(size_t words) {
    char *bp;
    size_t size;

    size = (words % 2) ? (words+1) * WSIZE : words * WSIZE;

    if (size < MIN_BLOCK_SIZE) {
        size = MIN_BLOCK_SIZE;
    }
    if ((long)(bp = mem_sbrk(size)) == -1)
        return NULL;

    /* Initialize free block header/footer and the epilogue header */
    PUT(HDRP(bp), PACK(size, 0)); /* Free block header */
    PUT(FTRP(bp), PACK(size, 0)); /* Free block footer */
    PUT(HDRP(NEXT_BLKP(bp)), PACK(0, 1));

    return coalesce(bp);
}

/*
* malloc
*/
void *malloc (size_t size) {
    size_t asize; // Adjusted block size
    size_t extendsize; // Amount to extend heap if no fit
    char *bp;

    if (size <= 0)
        return NULL;

    /* Ensures calls to sizes like 2 or 5 bytes are rounded towards
    ceiling of minimum block size, 24 bytes, to accomodate header, 
    pointers, and footer. */
    asize = MAX(ALIGN(size) + DSIZE, MIN_BLOCK_SIZE);

    // Search free list for a fit
    if ((bp = find_fit(asize))) {
        place(bp, asize);
        return bp;
    }

    // No fit found, get more memory and place the block
    extendsize = MAX(asize, CHUNKSIZE);
    if ((bp = extend_heap(extendsize/WSIZE)) == NULL)
        return NULL;
    place(bp, asize);
    return bp;
}

/* Performs first fit search on the free list, selecting first block 
with size greater than or equal to asize, otherwise returning NULL 
if bo big enough block. */
static void *find_fit(size_t asize) {
    void *bp;
    /*void* best_fit = NULL;
    int best_fit_leftover = INT_MAX;
    unsigned size;
    int current_leftover;

    for (bp = free_listp; GET_ALLOC(HDRP(bp)) == 0; bp = NEXT_FREE_BLKP(bp)) {
        size = GET_SIZE(HDRP(bp));

        if (asize <= size) {
            current_leftover = GET_SIZE(HDRP(bp)) - asize;
            if (asize == size)
                return bp;
            else {
                if (current_leftover < best_fit_leftover) { 
                    best_fit = bp;
                    best_fit_leftover = current_leftover;
                }
                
            }
        }
    } */

    for (bp = free_listp; GET_ALLOC(HDRP(bp)) == 0; bp = NEXT_FREE_BLKP(bp)) {
        if (asize <= GET_SIZE(HDRP(bp)))
            return bp;
    } 
    return NULL;
}

/* Decides whether we can split the block, and if so performs the split
by computing leftover block space, deleting shortened allocated block, 
and then labeling split free block and coalescing. 
Otherwise, just resets size and allocation tags of block and deletes
it from free list. */
static void place(void *bp, size_t asize) {
    size_t csize = GET_SIZE(HDRP(bp));

    if ((csize - asize) >= MIN_BLOCK_SIZE) {
        PUT(HDRP(bp), PACK(asize, 1));
        PUT(FTRP(bp), PACK(asize, 1));
        deleteBlk(bp);
        bp = NEXT_BLKP(bp);
        PUT(HDRP(bp), PACK(csize-asize, 0));
        PUT(FTRP(bp), PACK(csize-asize, 0));
        coalesce(bp);
    }
    /* Not enoough room to split, simple allocation and free list deletion */
    else {
        PUT(HDRP(bp), PACK(csize, 1));
        PUT(FTRP(bp), PACK(csize, 1));
        deleteBlk(bp);
    }
}

/* "Removes" an allocated block from the free list by reassigning
the pointers */
static void deleteBlk(void *bp) {
    /* If the new allocated block is at the beginning of the free list,
    then change start of free list to next block, retain next block next ptr.

    Else change prev block next pointer to next block, change next block prev
    pointer to prev block. */

    if (PREV_FREE_BLKP(bp))
        NEXT_FREE_BLKP(PREV_FREE_BLKP(bp)) = NEXT_FREE_BLKP(bp);
    else
        free_listp = NEXT_FREE_BLKP(bp);
    PREV_FREE_BLKP(NEXT_FREE_BLKP(bp)) = PREV_FREE_BLKP(bp);
}

/*
* free
*/
void free (void *bp) {
    if (!bp) return;
    size_t size = GET_SIZE(HDRP(bp));

    PUT(HDRP(bp), PACK(size, 0));
    PUT(FTRP(bp), PACK(size, 0));
    coalesce(bp);
}

/* Looks to the right and to the left to combine with nearby free blocks
in order to minimize fragmentation. */
static void *coalesce(void *bp) {
    size_t prev_alloc = GET_ALLOC(FTRP(PREV_BLKP(bp))) || PREV_BLKP(bp) == bp;
    size_t next_alloc = GET_ALLOC(HDRP(NEXT_BLKP(bp)));
    size_t size = GET_SIZE(HDRP(bp));

    /* Coalesce with block to the right */
    if (prev_alloc && !next_alloc) {
        size += GET_SIZE(HDRP(NEXT_BLKP(bp)));
        /* Now remove coalesced block to make room for actual coalesce */
        deleteBlk(NEXT_BLKP(bp));
        PUT(HDRP(bp), PACK(size, 0));
        PUT(FTRP(bp), PACK(size, 0));
    }
    /* Coalesce with block to the left */
    else if (!prev_alloc && next_alloc) {
        size += GET_SIZE(HDRP(PREV_BLKP(bp)));
        bp = PREV_BLKP(bp);
        deleteBlk(bp); // Delete previous blck to make room
        PUT(HDRP(bp), PACK(size, 0));
        PUT(FTRP(bp), PACK(size, 0));
    }
    /* Coalesce with both left and right blocks */
    else if (!prev_alloc && !next_alloc) {
        size += GET_SIZE(HDRP(PREV_BLKP(bp))) +
                GET_SIZE(HDRP(NEXT_BLKP(bp)));
        /* Deletes next and previous blocks to make more room,
        then reassigns bp to reflect coalescing */
        deleteBlk(PREV_BLKP(bp));
        deleteBlk(NEXT_BLKP(bp));
        bp = PREV_BLKP(bp);
        PUT(HDRP(bp), PACK(size, 0));
        PUT(FTRP(bp), PACK(size, 0));
    }

    /* Insert newly freed block at the front of free list */
    reinsert(bp);

    return bp;
}

/* Takes a newly freed, coalesced block and inserts it at the front
of the free list, to maintain minimal fragmentation. */
static void reinsert(void *bp) {
    /* Modify original free list start pointers
    Change newly inserted free block pointers accordingly */
    NEXT_FREE_BLKP(bp) = free_listp;
    PREV_FREE_BLKP(free_listp) = bp;
    PREV_FREE_BLKP(bp) = NULL;
    /* Reassign start of free list to block bp */
    free_listp = bp;
}

/*
* realloc - you may want to look at mm-naive.c
*/
void *realloc(void *bp, size_t size) {
    size_t old_size;
    void *new_bp;
    size_t asize = MAX(ALIGN(size) + DSIZE, MIN_BLOCK_SIZE);
    size_t split_size;

    /* Basically a call to free */
    if (size <= 0) {
        free(bp);
        return NULL;
    }

    /* bp hasn't even been malloc'd, so malloc it */
    if (bp == NULL) return malloc(size);

    old_size = GET_SIZE(HDRP(bp));

    /* No change needed */
    if (asize == old_size) return bp;

    /* Reallocation to a smaller size, so split the block and split
    the new unused portion */
    if (asize < old_size) {
        split_size = old_size - asize;
        if (split_size < MIN_BLOCK_SIZE) return bp;

        PUT(HDRP(bp), PACK(asize, 1));
        PUT(FTRP(bp), PACK(asize, 1));
        PUT(HDRP(NEXT_BLKP(bp)), PACK(split_size, 1));
        free(NEXT_BLKP(bp));
        return bp;
    }

    new_bp = malloc(asize);

    /* ALways check for malloc failure */
    if (new_bp == NULL) return bp;

    if (size < old_size) old_size = size;

    memcpy(new_bp, bp, old_size);

    /* Free old malloc'd pointer */
    free(bp);

    return new_bp;
}

/*
* calloc - you may want to look at mm-naive.c
* This function is not tested by mdriver, but it is
* needed to run the traces.
*/
void *calloc (size_t nmemb, size_t size) {

    size_t bytes = nmemb * size;
    void *newptr;

    newptr = malloc(bytes);
    memset(newptr, 0, bytes);

    return newptr;
}


/*
* Return whether the pointer is in the heap.
* May be useful for debugging.
*/
static int in_heap(const void *p) {
return p <= mem_heap_hi() && p >= mem_heap_lo();
}

/*
* Return whether the pointer is aligned.
* May be useful for debugging.
*/
static int aligned(const void *p) {
return (size_t)ALIGN(p) == (size_t)p;
}

/*
* mm_checkheap
*/
void mm_checkheap(int lineno) {
    lineno = lineno;

    int free_count = 0;
    int freelist_count = 0;
    void *bp;

    for (bp = free_listp; GET_SIZE(HDRP(bp)) > 0; bp = NEXT_FREE_BLKP(bp)) {
        if (GET_ALLOC(bp)) 
            printf("Allocated block in free list!\n");
        if (!aligned(bp)) printf("Base pointer in heap is not aligned!\n");
        if (!in_heap(NEXT_FREE_BLKP(bp)) || !in_heap(PREV_FREE_BLKP(bp))) 
            printf("Pointer not in heap! Uh oh.\n");
        if (GET(HDRP(bp)) != GET(FTRP(bp))) 
            printf("Header and footer don't match! Dang...\n");
        if (PREV_FREE_BLKP(NEXT_FREE_BLKP(bp)) != bp || 
            NEXT_FREE_BLKP(PREV_FREE_BLKP(bp)) != bp)
            printf("Pointers do not match up! Ugh\n");
        freelist_count++;
    }

    for (bp = free_listp; GET_SIZE(HDRP(bp)) > 0; bp = NEXT_BLKP(bp)) {
        if (!aligned(bp)) printf("Base pointer in heap is not aligned!\n");
        if (GET(HDRP(bp)) != GET(FTRP(bp))) 
            printf("Header and footer don't match! Dang...\n");
        if (PREV_BLKP(NEXT_BLKP(bp)) != bp || NEXT_BLKP(PREV_BLKP(bp)) != bp)
            printf("Pointers do not match up! Ugh\n");
        if (!GET_ALLOC(HDRP(bp))) free_count++;
    }

    if (free_count != freelist_count) 
        printf("Free blocks in free list don't match up with heap traversal!");

}
