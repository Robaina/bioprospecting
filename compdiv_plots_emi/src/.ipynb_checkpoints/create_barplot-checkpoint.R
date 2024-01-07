create_barplot <- function(TBL_ext = TBL_ext, TBL_div = TBL_div, bgc_colors = bgc_colors, text_size = 12) {

  barplot <- ggplot(TBL_ext, aes(x = sample, y = abund_rel, fill = bgc_class)) + 
             geom_bar(stat = "identity", width = 0.5, alpha = 0.7) +
             xlab("Sample") +
             ylab("Percentage of abundance") +
             scale_fill_manual(name="BGC class",
                               values = bgc_colors) +
             scale_y_continuous(expand=c(0,0.1), limits = c(-1,101), 
                                sec.axis = sec_axis(~.*(max(TBL_div$shannon)/101), name = "Shannon diversity")) +
             theme_light() +
             theme( 
                   axis.text.x = element_text(size = text_size -2, angle = 45, 
                                              hjust = 1, color = "black"),
                   axis.text.y = element_text(size = text_size, color = "black"),
                   axis.title.x = element_text(size = text_size + 4, color = "black",
                                               margin = margin(10,0,0,0)),
                   axis.title.y = element_text(size = text_size + 4, color = "black",
                                               margin = margin(0,15,0,0)),
                   legend.text = element_text(size = text_size +2, color = "black"),
                   legend.title = element_text(size = text_size +4 , color = "black"),
                   legend.position = "right",
                   legend.margin = ggplot2::margin(0,0,-5,0),
                   strip.background = element_blank(),
                   strip.text = element_text(color = "black", size = text_size)) +
                   guides(fill = guide_legend(keywidth = 0.6, keyheight = 0.6)) +
            geom_line(data = TBL_div, aes(y = shannon*(99/1.5), fill = NULL, group = 1),
                     linewidth = 1.5) 
    
  return(barplot)
}
