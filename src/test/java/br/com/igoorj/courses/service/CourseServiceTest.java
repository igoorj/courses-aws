package br.com.igoorj.courses.service;

import br.com.igoorj.courses.dto.CourseRequest;
import br.com.igoorj.courses.entity.Course;
import br.com.igoorj.courses.repository.CourseRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class CourseServiceTest {

    @Mock
    private CourseRepository courseRepository;

    @InjectMocks
    private CourseService courseService;

    @Test
    void findAll_shouldReturnAllCourses() {
        var course1 = buildCourse(1L, "AWS Fundamentals", "Intro to AWS");
        var course2 = buildCourse(2L, "Spring Boot", "API REST com Spring");

        when(courseRepository.findAll()).thenReturn(List.of(course1, course2));

        List<Course> result = courseService.findAll();

        assertThat(result).hasSize(2);
        assertThat(result).containsExactly(course1, course2);
        verify(courseRepository).findAll();
    }

    @Test
    void findAll_shouldReturnEmptyList_whenNoCourses() {
        when(courseRepository.findAll()).thenReturn(List.of());

        List<Course> result = courseService.findAll();

        assertThat(result).isEmpty();
        verify(courseRepository).findAll();
    }

    @Test
    void create_shouldMapRequestAndSaveCourse() {
        var request = new CourseRequest("AWS Fundamentals", "Intro to AWS");
        var saved = buildCourse(1L, request.name(), request.description());

        when(courseRepository.save(any(Course.class))).thenReturn(saved);

        Course result = courseService.create(request);

        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("AWS Fundamentals");
        assertThat(result.getDescription()).isEqualTo("Intro to AWS");
        verify(courseRepository).save(any(Course.class));
    }

    private Course buildCourse(Long id, String name, String description) {
        var course = new Course();
        course.setId(id);
        course.setName(name);
        course.setDescription(description);
        return course;
    }
}
