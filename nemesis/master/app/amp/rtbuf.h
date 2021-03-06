/*****************************************************************************/

/*
 *      rtbuf.h  --  Linux realtime audio output.
 *
 *      Copyright (C) 1996  Thomas Sailer (sailer@ife.ee.ethz.ch)
 *
 *      This program is free software; you can redistribute it and/or modify
 *      it under the terms of the GNU General Public License as published by
 *      the Free Software Foundation; either version 2 of the License, or
 *      (at your option) any later version.
 *
 *      This program is distributed in the hope that it will be useful,
 *      but WITHOUT ANY WARRANTY; without even the implied warranty of
 *      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *      GNU General Public License for more details.
 *
 *      You should have received a copy of the GNU General Public License
 *      along with this program; if not, write to the Free Software
 *      Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 *
 *  This is the Linux realtime sound output driver
 */

/*****************************************************************************/

#ifndef HAVE_MLOCKALL
#undef LINUX_REALTIME
#endif

#ifndef HAVE_SCHED_SETSCHEDULER
#undef LINUX_REALTIME
#endif

#if 0
#ifndef _POSIX_MEMLOCK
#undef LINUX_REALTIME
#endif

#ifndef _POSIX_PRIORITY_SCHEDULING
#undef LINUX_REALTIME
#endif
#endif

#ifdef LINUX_REALTIME

int  prefetch_get_input(unsigned char *bp, int bytes);
int  rt_play(char *file);
void rt_printout(short *sbuf, int ln);
int 	setup_fancy_audio(struct AUDIO_HEADER *mpegheader);
int 	start_fancy_audio(struct AUDIO_HEADER *mpegheader);
int  	 stop_fancy_audio(void);
int 	block_fancy_audio(int snd_eof);
int 	ready_fancy_audio(void);
void  cleanup_fancy_audio(void);
void prefetch_initial_fill(void);
int set_realtime_priority(void);

#endif /* LINUX_REALTIME */

