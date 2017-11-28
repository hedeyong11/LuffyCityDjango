from arya.service import sites

from . import models

sites.site.register(models.User)
sites.site.register(models.CourseCategory)
sites.site.register(models.CourseSubCategory)
sites.site.register(models.DegreeCourse)
sites.site.register(models.Scholarship)
sites.site.register(models.Course)
sites.site.register(models.CourseDetail)
sites.site.register(models.OftenAskedQuestion)
sites.site.register(models.CourseOutline)
sites.site.register(models.CourseChapter)
sites.site.register(models.Teacher)
sites.site.register(models.PricePolicy)#需配置
sites.site.register(models.CourseSection)